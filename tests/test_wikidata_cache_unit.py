# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the persistent Wikidata cache in ``knowledge/public/cache.py``.

Two failures live here, and both are silent — the cache keeps answering, it just answers
with less than it stored:

* ``WikidataClass.as_dict`` writes the subclass tree but ``create_from_dict`` only read the
  superclass tree back, so every persisted class returned as a leaf. The ontology mapping
  builds its class index from those hierarchies, so a warm cache produced a drastically
  smaller index than a cold one and mapped entities to different concept types.
* A QID that Wikidata redirects is cached under the id it resolves to, never under the id
  that was asked for, so the lookup misses forever and every reference re-fetches.

No network — every class is built with an explicit label, because ``WikidataClass.label``
lazily fetches when it is None.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytest

from knowledge.base.entity import Label
from knowledge.base.language import EN_US
from knowledge.public import client as client_module
from knowledge.public.cache import WikidataCache
from knowledge.public.client import WikiDataAPIClient
from knowledge.public.wikidata import WikidataClass, WikidataThing

ORGANIZATION: str = "Q43229"
COMPANY: str = "Q4830453"
NONPROFIT: str = "Q163740"
AGENCY: str = "Q327333"

REDIRECTED_QID: str = "Q18220463"
CANONICAL_QID: str = "Q1255283"


@pytest.fixture(autouse=True)
def _isolated_cache() -> Any:
    """Each test gets an empty singleton, so nothing leaks between them."""
    cache: WikidataCache = WikidataCache()
    cache.cache.clear()
    cache.property_cache.clear()
    cache.subclass_cache.clear()
    cache.superclass_cache.clear()
    cache.redirect_cache.clear()
    yield cache
    cache.cache.clear()
    cache.subclass_cache.clear()
    cache.redirect_cache.clear()


def _hierarchy() -> WikidataClass:
    """``organization`` with two subclasses, one of which has a subclass of its own."""
    organization: WikidataClass = WikidataClass(ORGANIZATION, "organization")
    company: WikidataClass = WikidataClass(COMPANY, "company")
    nonprofit: WikidataClass = WikidataClass(NONPROFIT, "nonprofit organization")
    agency: WikidataClass = WikidataClass(AGENCY, "government agency")
    company.subclasses.append(agency)
    organization.subclasses.append(company)
    organization.subclasses.append(nonprofit)
    return organization


def _descendants(node: WikidataClass) -> List[str]:
    """Every QID reachable through the subclass edges, depth first."""
    found: List[str] = []
    for subclass in node.subclasses:
        found.append(subclass.qid)
        found.extend(_descendants(subclass))
    return found


# ------------------------------------------ Subclass round-trip -------------------------------------------------------
def test_subclass_tree_survives_the_dictionary_round_trip() -> None:
    """``as_dict`` writes the subclass tree, so ``create_from_dict`` must read it back.

    Dropping it turns every persisted class into a leaf, which is what collapsed the
    ontology mapping's class index once a cache had been written to disk.
    """
    original: WikidataClass = _hierarchy()

    restored: WikidataClass = WikidataClass.create_from_dict(original.as_dict())

    assert sorted(_descendants(restored)) == sorted(_descendants(original))
    assert sorted(_descendants(restored)) == sorted([COMPANY, AGENCY, NONPROFIT])


def test_nested_subclass_labels_survive_the_round_trip() -> None:
    """Labels must come back too, or the restored tree triggers lazy network lookups."""
    restored: WikidataClass = WikidataClass.create_from_dict(_hierarchy().as_dict())

    by_qid: Dict[str, WikidataClass] = {node.qid: node for node in restored.subclasses}
    assert by_qid[COMPANY].label == "company"
    assert by_qid[NONPROFIT].label == "nonprofit organization"
    assert by_qid[COMPANY].subclasses[0].label == "government agency"


def test_superclass_tree_still_survives_the_round_trip() -> None:
    """The superclass direction already worked and must keep working."""
    organization: WikidataClass = WikidataClass(ORGANIZATION, "organization")
    agent: WikidataClass = WikidataClass("Q24229398", "agent")
    organization.superclasses.append(agent)

    restored: WikidataClass = WikidataClass.create_from_dict(organization.as_dict())

    assert [node.qid for node in restored.superclasses] == ["Q24229398"]


def test_a_cyclic_hierarchy_round_trips_without_recursing_forever() -> None:
    """Wikidata's class graph has cycles; the visited guard must keep the restore finite."""
    first: WikidataClass = WikidataClass("Q1", "first")
    second: WikidataClass = WikidataClass("Q2", "second")
    first.subclasses.append(second)
    second.subclasses.append(first)

    restored: WikidataClass = WikidataClass.create_from_dict(first.as_dict())

    assert [node.qid for node in restored.subclasses] == ["Q2"]
    assert restored.subclasses[0].subclasses == []


def test_subclass_cache_survives_save_and_load(tmp_path: Path) -> None:
    """The whole point of the cache: what goes to disk must come back."""
    cache: WikidataCache = WikidataCache()
    cache.subclass_cache[ORGANIZATION] = _hierarchy()
    cache.save_cache(tmp_path)
    cache.subclass_cache.clear()

    cache.load_cache(tmp_path)

    assert sorted(_descendants(cache.get_subclass(ORGANIZATION))) == sorted([COMPANY, AGENCY, NONPROFIT])


# --------------------------------------------- Redirected QIDs --------------------------------------------------------
def _thing(qid: str) -> WikidataThing:
    """A minimal cacheable entity."""
    return WikidataThing(
        revision="1",
        qid=qid,
        modified=datetime(2026, 1, 1),
        label={"en_US": Label("Redirect target", EN_US, main=True)},
    )


def test_a_redirected_qid_is_cached_under_the_id_that_was_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    """Asking for a redirected QID twice must hit the cache the second time.

    Wikidata resolves redirects silently, so the entity arrives under a different id.
    Caching it only under that id leaves the requested id permanently absent, and every
    reference to it re-fetches — three times in a few seconds on a real crawl.
    """
    calls: List[str] = []

    def fake_request(qid: str) -> Dict[str, Any]:
        calls.append(qid)
        return {
            "id": CANONICAL_QID,
            "lastrevid": 1,
            "modified": "2026-01-01T00:00:00Z",
            "labels": {"en": {"language": "en", "value": "Redirect target"}},
            "descriptions": {},
            "aliases": {},
            "claims": {},
            "sitelinks": {},
        }

    monkeypatch.setattr(client_module, "__waiting_request__", fake_request)

    first: WikidataThing = WikiDataAPIClient.retrieve_entity(REDIRECTED_QID)
    second: WikidataThing = WikiDataAPIClient.retrieve_entity(REDIRECTED_QID)

    assert first.qid == CANONICAL_QID
    assert second.qid == CANONICAL_QID
    assert calls == [REDIRECTED_QID], "the second lookup must be served from the cache"


def test_the_cache_reports_a_redirected_qid_as_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """``qid_in_cache`` is what callers branch on, so it must resolve the redirect."""

    def fake_request(qid: str) -> Dict[str, Any]:
        return {
            "id": CANONICAL_QID,
            "lastrevid": 1,
            "modified": "2026-01-01T00:00:00Z",
            "labels": {"en": {"language": "en", "value": "Redirect target"}},
            "descriptions": {},
            "aliases": {},
            "claims": {},
            "sitelinks": {},
        }

    monkeypatch.setattr(client_module, "__waiting_request__", fake_request)
    WikiDataAPIClient.retrieve_entity(REDIRECTED_QID)

    cache: WikidataCache = WikidataCache()
    assert cache.qid_in_cache(CANONICAL_QID)
    assert cache.qid_in_cache(REDIRECTED_QID)
    assert cache.get_wikidata_object(REDIRECTED_QID).qid == CANONICAL_QID


def test_redirects_survive_save_and_load(tmp_path: Path) -> None:
    """A redirect learned in one run must not be re-learned in the next."""
    cache: WikidataCache = WikidataCache()
    cache.cache_wikidata_object(_thing(CANONICAL_QID))
    cache.cache_redirect(REDIRECTED_QID, CANONICAL_QID)
    cache.save_cache(tmp_path)
    cache.cache.clear()
    cache.redirect_cache.clear()

    cache.load_cache(tmp_path)

    assert cache.qid_in_cache(REDIRECTED_QID)
    assert cache.get_wikidata_object(REDIRECTED_QID).qid == CANONICAL_QID


def test_an_unknown_qid_is_still_absent() -> None:
    """The redirect resolution must not make every lookup report a hit."""
    cache: WikidataCache = WikidataCache()

    assert not cache.qid_in_cache("Q999999999")
