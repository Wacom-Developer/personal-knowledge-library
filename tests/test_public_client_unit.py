# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the Wikidata connector in ``knowledge/public/client.py``.

No network and no server required — the SPARQL / API layer is replaced by stubs so the
tests exercise the connector's own control flow.
"""

from datetime import datetime
from typing import Any, Dict, List

import pytest

from knowledge.base.language import EN
from knowledge.public import client as client_module
from knowledge.public.client import WikiDataAPIClient
from knowledge.public.wikidata import WikidataThing


@pytest.fixture(autouse=True)
def _clear_sparql_caches() -> Any:
    """Keep the module-level LRU caches from leaking between tests."""
    WikiDataAPIClient._superclasses_cached.cache_clear()
    WikiDataAPIClient._subclasses_cached.cache_clear()
    yield
    WikiDataAPIClient._superclasses_cached.cache_clear()
    WikiDataAPIClient._subclasses_cached.cache_clear()


def _entity_payload(qid: str) -> Dict[str, Any]:
    """A minimal but structurally complete ``wbgetentities`` payload."""
    return {
        "id": qid,
        "lastrevid": 1,
        "modified": "2026-01-01T00:00:00Z",
        "labels": {"en": {"language": "en", "value": f"Label of {qid}"}},
        "descriptions": {},
        "aliases": {},
        "claims": {},
        "sitelinks": {},
    }


# --------------------------------------- retrieve_entities ------------------------------------------------------------
def test_retrieve_entities_returns_empty_when_every_qid_is_filtered_out() -> None:
    """Nothing left to fetch must yield an empty result, not an IndexError.

    ``retrieve_entities`` drops QIDs that are already cached or malformed. When that
    removes every entry there is no chunk to dispatch.
    """
    assert WikiDataAPIClient.retrieve_entities(["not-a-qid"]) == []


def test_retrieve_entities_fetches_the_missing_qids(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every QID handed to the connector comes back, across more than one chunk."""
    requested: List[List[str]] = []

    def fake_multi_request(qids: List[str]) -> List[Dict[str, Any]]:
        requested.append(list(qids))
        return [_entity_payload(qid) for qid in qids]

    monkeypatch.setattr(client_module, "__waiting_multi_request__", fake_multi_request)
    monkeypatch.setattr(client_module, "API_LIMIT", 2)
    monkeypatch.setattr(client_module.wikidata_cache, "qid_in_cache", lambda qid: False)
    monkeypatch.setattr(client_module.wikidata_cache, "cache_wikidata_object", lambda thing: None)

    pulled = WikiDataAPIClient.retrieve_entities(["Q1", "Q2", "Q3", "Q4", "Q5"])

    assert sorted(thing.qid for thing in pulled) == ["Q1", "Q2", "Q3", "Q4", "Q5"]
    assert sorted(sum(requested, [])) == ["Q1", "Q2", "Q3", "Q4", "Q5"]


def test_retrieve_entities_reports_progress_for_every_entity(monkeypatch: pytest.MonkeyPatch) -> None:
    """The progress callback ends at the total number of requested entities."""
    monkeypatch.setattr(
        client_module,
        "__waiting_multi_request__",
        lambda qids: [_entity_payload(qid) for qid in qids],
    )
    monkeypatch.setattr(client_module.wikidata_cache, "qid_in_cache", lambda qid: False)
    monkeypatch.setattr(client_module.wikidata_cache, "cache_wikidata_object", lambda thing: None)
    reported: List[tuple] = []

    WikiDataAPIClient.retrieve_entities(["Q1", "Q2"], progress=lambda done, total: reported.append((done, total)))

    assert reported[-1] == (2, 2)


# ------------------------------------------- search_term --------------------------------------------------------------
class _StubResponse:
    """Minimal stand-in for ``requests.Response``."""

    def __init__(self, payload: Dict[str, Any]) -> None:
        self.__payload = payload
        self.status_code = 200
        self.ok = True

    def json(self) -> Dict[str, Any]:
        return self.__payload


def _search_hit(qid: str, label: str) -> Dict[str, Any]:
    """A minimal but structurally complete ``wbsearchentities`` hit."""
    return {
        "id": qid,
        "repository": "wikidata",
        "display": {"label": {"language": "en", "value": label}},
    }


def _stub_search(monkeypatch: pytest.MonkeyPatch, hits: List[Dict[str, Any]]) -> None:
    monkeypatch.setattr(
        client_module._wikidata_session,
        "get",
        lambda *args, **kwargs: _StubResponse({"search": hits}),
    )


def test_search_term_returns_every_hit(monkeypatch: pytest.MonkeyPatch) -> None:
    """All search results are returned, not just the first one."""
    _stub_search(
        monkeypatch,
        [
            _search_hit("Q1", "first"),
            _search_hit("Q2", "second"),
            _search_hit("Q3", "third"),
        ],
    )

    results = WikiDataAPIClient.search_term("anything", EN)

    assert [result.qid for result in results] == ["Q1", "Q2", "Q3"]


def test_search_term_returns_an_empty_list_when_nothing_matches(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty result set is an empty list, never None."""
    _stub_search(monkeypatch, [])

    assert WikiDataAPIClient.search_term("anything", EN) == []


# ------------------------------------------- SPARQL caching -----------------------------------------------------------
def test_a_failed_superclass_lookup_is_not_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    """A transient SPARQL failure must not poison the cache for the process lifetime."""
    calls: List[str] = []

    def flaky_query(query: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        calls.append(query)
        if len(calls) == 1:
            raise ConnectionError("wikidata is having a moment")
        return {
            "results": {
                "bindings": [
                    {
                        "class": {"value": "http://www.wikidata.org/entity/Q5"},
                        "classLabel": {"value": "human"},
                        "superclass": {"value": "http://www.wikidata.org/entity/Q215627"},
                        "superclassLabel": {"value": "person"},
                    }
                ]
            }
        }

    monkeypatch.setattr(WikiDataAPIClient, "sparql_query", staticmethod(flaky_query))

    first = WikiDataAPIClient.superclasses("Q5")
    second = WikiDataAPIClient.superclasses("Q5")

    assert len(calls) == 2, "the failed lookup was served from the cache"
    assert set(first) == {"Q5"}, "the failed lookup degrades to the bare fallback"
    assert "Q215627" in second, "the retry did not reach the service"


def test_a_successful_superclass_lookup_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    """Repeated lookups of the same QID issue a single SPARQL query."""
    calls: List[str] = []

    def counting_query(query: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        calls.append(query)
        return {"results": {"bindings": []}}

    monkeypatch.setattr(WikiDataAPIClient, "sparql_query", staticmethod(counting_query))

    WikiDataAPIClient.superclasses("Q5")
    WikiDataAPIClient.superclasses("Q5")

    assert len(calls) == 1


def test_superclasses_is_served_by_the_cached_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    """``superclasses`` delegates to ``_superclasses_cached`` — guards the dead duplicate."""
    monkeypatch.setattr(
        WikiDataAPIClient,
        "_superclasses_cached",
        staticmethod(lambda qid: (("Q5", "Q215627", "human", "person"),)),
    )

    hierarchy = WikiDataAPIClient.superclasses("Q5")

    assert set(hierarchy) == {"Q5", "Q215627"}
    assert [cls.qid for cls in hierarchy["Q5"].superclasses] == ["Q215627"]


# --------------------------------------------- hashing ---------------------------------------------------------------
def test_wikidata_things_with_different_qids_hash_differently() -> None:
    """A constant hash turns every set/dict of things into a linear scan."""
    things = [WikidataThing(revision="1", qid=f"Q{idx}", modified=datetime.now()) for idx in range(64)]

    assert len({hash(thing) for thing in things}) > 1


def test_wikidata_thing_hash_agrees_with_equality() -> None:
    """Equal things must hash equally, so deduplication through a set works."""
    left = WikidataThing(revision="1", qid="Q42", modified=datetime.now())
    right = WikidataThing(revision="2", qid="Q42", modified=datetime.now())

    assert left == right
    assert hash(left) == hash(right)
    assert len({left, right}) == 1


# ------------------------------------------ retry budget --------------------------------------------------------------
def test_the_wikidata_retry_budget_is_bounded() -> None:
    """A rate-limited endpoint must not be able to stall a bulk import for minutes.

    Wikidata answers 429 readily, and with `respect_retry_after_header` an unbounded
    backoff lets a single call block far longer than the caller's own timeout.
    """
    policy = client_module._retry_policy

    worst_case = sum(policy.backoff_factor * (2**attempt) for attempt in range(policy.total))
    assert policy.backoff_max <= 20
    assert worst_case <= 60, f"worst-case backoff is {worst_case}s"
