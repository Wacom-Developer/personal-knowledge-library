# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for how ``knowledge/utils/diff.py`` resolves relation targets.

``ObjectProperty.incoming_relations`` / ``outgoing_relations`` are typed
``List[Union[str, ThingObject]]`` and hold whichever form produced them: the NDJSON import
format carries bare URI strings, while ``GET /entity/{uri}/relations`` answers with full
entity objects. The diff looks each target up in a ``Dict[str, ThingObject]``, so it has to
reduce an entity-shaped target to its URI first — otherwise the lookup misses and the diff
reports a target as missing when it is present.

Also covers ``ThingObject`` hashing, which the diff relies on indirectly through the
dictionaries and sets it builds. No server required — the client is a mock.
"""

import time
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge.base.entity import Label
from knowledge.base.language import EN_US
from knowledge.base.ontology import (
    ObjectProperty,
    OntologyClassReference,
    OntologyPropertyReference,
    ThingObject,
)
from knowledge.utils.diff import diff_entities, diff_entities_async

THING_CLASS: OntologyClassReference = OntologyClassReference.parse("wacom:core#Thing")
RELATED_TO: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#relatedTo")

SOURCE_URI: str = "wacom:entity:source"
TARGET_URI: str = "wacom:entity:target"


def _thing(uri: str, label: str = "Test Entity") -> ThingObject:
    thing: ThingObject = ThingObject(
        uri=uri,
        label=[Label(label, EN_US, main=True)],
        concept_type=THING_CLASS,
    )
    thing.reference_id = f"ref-{uri}"
    return thing


def _relation(targets: List[object], incoming: bool = False) -> ObjectProperty:
    """Build an ObjectProperty holding the given targets, in either direction."""
    prop: ObjectProperty = ObjectProperty(relation=RELATED_TO)
    for target in targets:
        if incoming:
            prop.incoming_relations.append(target)  # type: ignore[arg-type]
        else:
            prop.outgoing_relations.append(target)  # type: ignore[arg-type]
    return prop


def _client_returning(relations: Dict[OntologyPropertyReference, ObjectProperty]) -> MagicMock:
    client: MagicMock = MagicMock()
    client.relations.return_value = relations
    return client


# ------------------------------------------ target resolution ---------------------------------------------------------
@pytest.mark.parametrize("incoming", [False, True], ids=["outgoing", "incoming"])
def test_a_uri_shaped_target_that_is_linked_is_not_reported(incoming: bool) -> None:
    """Baseline: a bare URI target that the graph also links is no difference."""
    target: ThingObject = _thing(TARGET_URI)
    file_thing: ThingObject = _thing(SOURCE_URI)
    file_thing.object_properties[RELATED_TO] = _relation([TARGET_URI], incoming=incoming)
    kg_thing: ThingObject = _thing(SOURCE_URI)
    client: MagicMock = _client_returning({RELATED_TO: _relation([TARGET_URI], incoming=incoming)})

    _, _, object_differences = diff_entities(client, file_thing, kg_thing, kg_things={TARGET_URI: target})

    assert object_differences == []


@pytest.mark.parametrize("incoming", [False, True], ids=["outgoing", "incoming"])
def test_an_entity_shaped_target_that_is_linked_is_not_reported(incoming: bool) -> None:
    """An entity-shaped target must resolve by its URI, not be reported as missing.

    ``client.relations()`` returns full entities, so a `file_thing` built from a service
    response carries `ThingObject` targets. Looking those up in a URI-keyed dictionary
    misses, and the diff then claims a target is missing while the graph links it.
    """
    target: ThingObject = _thing(TARGET_URI)
    file_thing: ThingObject = _thing(SOURCE_URI)
    file_thing.object_properties[RELATED_TO] = _relation([target], incoming=incoming)
    kg_thing: ThingObject = _thing(SOURCE_URI)
    client: MagicMock = _client_returning({RELATED_TO: _relation([target], incoming=incoming)})

    _, _, object_differences = diff_entities(client, file_thing, kg_thing, kg_things={TARGET_URI: target})

    assert object_differences == [], f"linked target reported as a difference: {object_differences}"


@pytest.mark.parametrize("incoming", [False, True], ids=["outgoing", "incoming"])
def test_an_entity_shaped_target_that_is_not_linked_is_reported(incoming: bool) -> None:
    """The check still fires when the graph genuinely does not link the target."""
    target: ThingObject = _thing(TARGET_URI)
    file_thing: ThingObject = _thing(SOURCE_URI)
    file_thing.object_properties[RELATED_TO] = _relation([target], incoming=incoming)
    kg_thing: ThingObject = _thing(SOURCE_URI)
    client: MagicMock = _client_returning({RELATED_TO: _relation([], incoming=incoming)})

    _, _, object_differences = diff_entities(client, file_thing, kg_thing, kg_things={TARGET_URI: target})

    assert [d["type"] for d in object_differences] == ["Object properties target not linked"]


@pytest.mark.parametrize("incoming", [False, True], ids=["outgoing", "incoming"])
def test_a_target_absent_from_the_graph_is_reported(incoming: bool) -> None:
    """A target the graph does not know at all is still reported as missing."""
    file_thing: ThingObject = _thing(SOURCE_URI)
    file_thing.object_properties[RELATED_TO] = _relation([_thing("wacom:entity:unknown")], incoming=incoming)
    kg_thing: ThingObject = _thing(SOURCE_URI)
    client: MagicMock = _client_returning({RELATED_TO: _relation([], incoming=incoming)})

    _, _, object_differences = diff_entities(client, file_thing, kg_thing, kg_things={TARGET_URI: _thing(TARGET_URI)})

    assert [d["type"] for d in object_differences] == ["Object properties target missing"]


async def test_the_async_diff_resolves_entity_shaped_targets_too() -> None:
    """Sync and async must agree — they are duplicated implementations."""
    target: ThingObject = _thing(TARGET_URI)
    file_thing: ThingObject = _thing(SOURCE_URI)
    file_thing.object_properties[RELATED_TO] = _relation([target])
    kg_thing: ThingObject = _thing(SOURCE_URI)
    client: AsyncMock = AsyncMock()
    client.relations.return_value = {RELATED_TO: _relation([target])}

    _, _, object_differences = await diff_entities_async(client, file_thing, kg_thing, kg_things={TARGET_URI: target})

    assert object_differences == []


# ------------------------------------------ ThingObject hashing -------------------------------------------------------
def test_things_with_different_uris_hash_differently() -> None:
    """A constant hash turns every set or dict of entities into a linear scan."""
    things: List[ThingObject] = [_thing(f"wacom:entity:{idx}") for idx in range(64)]

    assert len({hash(thing) for thing in things}) > 1


def test_the_hash_agrees_with_equality() -> None:
    """Equal entities must hash equally, or a set would keep duplicates."""
    left: ThingObject = _thing(TARGET_URI)
    right: ThingObject = _thing(TARGET_URI)

    assert left == right
    assert hash(left) == hash(right)
    assert len({left, right}) == 1


def test_an_entity_without_a_uri_is_hashable() -> None:
    """Entities are hashed before they are created server-side, when the URI is still None."""
    unsaved: ThingObject = ThingObject(concept_type=THING_CLASS)

    assert isinstance(hash(unsaved), int)
    assert len({unsaved}) == 1


def test_building_a_set_of_entities_is_not_quadratic() -> None:
    """Guards the hash: a constant hash makes this take hundreds of times longer.

    Measured at 1500 entities: 95 ms with a constant hash against 0.15 ms with a real one.
    The bound is deliberately loose so the test is about the complexity class, not the
    machine it runs on.
    """
    things: List[ThingObject] = [_thing(f"wacom:entity:{idx}") for idx in range(1500)]

    start: float = time.perf_counter()
    collected = set(things)
    elapsed: float = time.perf_counter() - start

    assert len(collected) == 1500
    assert elapsed < 0.05, f"building a set of 1500 entities took {elapsed * 1000:.0f} ms"
