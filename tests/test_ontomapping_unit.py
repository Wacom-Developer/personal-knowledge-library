# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the Wikidata → PKS class index in ``knowledge/ontomapping``.

No network and no server required — the subclass lookup is stubbed and the subclass cache
is seeded directly.
"""

from typing import Any, Dict, List

import pytest

from knowledge.ontomapping import ClassConfiguration, MappingConfiguration
from knowledge.public.cache import WikidataCache
from knowledge.public.client import WikiDataAPIClient
from knowledge.public.wikidata import WikidataClass

PERSON_QID: str = "Q215627"
POLITICIAN_QID: str = "Q82955"
MAYOR_QID: str = "Q30185"


def _hierarchy() -> WikidataClass:
    """``person`` with ``politician`` below it and ``mayor`` below that."""
    person: WikidataClass = WikidataClass(PERSON_QID, "person")
    politician: WikidataClass = WikidataClass(POLITICIAN_QID, "politician")
    mayor: WikidataClass = WikidataClass(MAYOR_QID, "mayor")
    politician.subclasses.append(mayor)
    person.subclasses.append(politician)
    return person


def _configuration() -> ClassConfiguration:
    configuration: ClassConfiguration = ClassConfiguration("wacom:core#Person")
    configuration.wikidata_classes = [PERSON_QID]
    return configuration


@pytest.fixture()
def _cold_cache(monkeypatch: pytest.MonkeyPatch) -> Any:
    """A subclass cache that reports every QID as absent."""
    cache: WikidataCache = WikidataCache()
    monkeypatch.setattr(cache, "subclass_in_cache", lambda qid: False)
    monkeypatch.setattr(cache, "cache_subclass", lambda subclass: None)
    yield cache


def test_a_cold_cache_indexes_every_qid_of_the_hierarchy(
    monkeypatch: pytest.MonkeyPatch, _cold_cache: WikidataCache
) -> None:
    """Baseline: asking the connector indexes the whole hierarchy by QID."""
    monkeypatch.setattr(WikiDataAPIClient, "subclasses", staticmethod(lambda qid: {PERSON_QID: _hierarchy()}))
    configuration: MappingConfiguration = MappingConfiguration()

    configuration.add_class(_configuration())

    assert configuration.guess_classed([POLITICIAN_QID]) is not None
    assert configuration.guess_classed([MAYOR_QID]) is not None


def test_a_warm_cache_indexes_the_same_qids_as_a_cold_one(monkeypatch: pytest.MonkeyPatch) -> None:
    """The cached path must index QID strings too, not WikidataClass objects.

    Otherwise the mapping works on the first run and silently stops working once the
    subclass cache has been populated or loaded from disk.
    """
    hierarchy: WikidataClass = _hierarchy()
    cache: WikidataCache = WikidataCache()
    monkeypatch.setattr(cache, "subclass_in_cache", lambda qid: qid == PERSON_QID)
    monkeypatch.setattr(cache, "get_subclass", lambda qid: hierarchy)

    def fail_on_lookup(qid: str) -> Dict[str, WikidataClass]:
        raise AssertionError("the connector must not be asked when the cache is warm")

    monkeypatch.setattr(WikiDataAPIClient, "subclasses", staticmethod(fail_on_lookup))
    configuration: MappingConfiguration = MappingConfiguration()

    configuration.add_class(_configuration())

    assert configuration.guess_classed([PERSON_QID]) is not None
    assert configuration.guess_classed([POLITICIAN_QID]) is not None, "subclass not indexed by QID"
    assert configuration.guess_classed([MAYOR_QID]) is not None, "transitive subclass not indexed by QID"


def test_the_configured_class_itself_is_always_resolvable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Whichever path populated the index, the configured Wikidata class resolves."""
    monkeypatch.setattr(WikiDataAPIClient, "subclasses", staticmethod(lambda qid: {PERSON_QID: _hierarchy()}))
    cache: WikidataCache = WikidataCache()
    monkeypatch.setattr(cache, "subclass_in_cache", lambda qid: False)
    monkeypatch.setattr(cache, "cache_subclass", lambda subclass: None)
    configuration: MappingConfiguration = MappingConfiguration()

    configuration.add_class(_configuration())

    resolved = configuration.guess_classed([PERSON_QID])
    assert resolved is not None
    assert resolved.ontology_class == "wacom:core#Person"


def test_dbpedia_classes_stay_indexed(monkeypatch: pytest.MonkeyPatch) -> None:
    """The DBpedia side of the configuration is indexed by name as before."""
    monkeypatch.setattr(WikiDataAPIClient, "subclasses", staticmethod(lambda qid: {}))
    cache: WikidataCache = WikidataCache()
    monkeypatch.setattr(cache, "subclass_in_cache", lambda qid: False)
    monkeypatch.setattr(cache, "cache_subclass", lambda subclass: None)
    configuration: MappingConfiguration = MappingConfiguration()
    class_configuration: ClassConfiguration = _configuration()
    class_configuration.dbpedia_classes = ["dbo:Person"]

    configuration.add_class(class_configuration)

    assert configuration.guess_classed(["dbo:Person"]) is not None


def test_conflicting_mappings_are_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two configurations claiming the same Wikidata class produce a warning."""
    monkeypatch.setattr(WikiDataAPIClient, "subclasses", staticmethod(lambda qid: {PERSON_QID: _hierarchy()}))
    cache: WikidataCache = WikidataCache()
    monkeypatch.setattr(cache, "subclass_in_cache", lambda qid: False)
    monkeypatch.setattr(cache, "cache_subclass", lambda subclass: None)
    warnings: List[str] = []
    monkeypatch.setattr("knowledge.ontomapping.logger.warning", lambda message: warnings.append(str(message)))
    configuration: MappingConfiguration = MappingConfiguration()

    configuration.add_class(_configuration())
    second: ClassConfiguration = ClassConfiguration("wacom:core#Organization")
    second.wikidata_classes = [PERSON_QID]
    configuration.add_class(second)

    assert any(POLITICIAN_QID in message for message in warnings)
