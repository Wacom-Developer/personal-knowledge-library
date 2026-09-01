# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the NDJSON bulk-import format in ``knowledge/utils/import_format.py``.

Pure file round-trips — no server required.
"""

from pathlib import Path
from typing import List

import pytest

from knowledge.base.language import EN_US
from knowledge.base.ontology import OntologyClassReference, ThingObject
from knowledge.utils.import_format import (
    iterate_large_import_format,
    load_import_format,
    save_import_format,
)

PERSON: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")


def _things(count: int) -> List[ThingObject]:
    entities: List[ThingObject] = []
    for idx in range(count):
        thing: ThingObject = ThingObject(concept_type=PERSON)
        thing.add_label(f"Person {idx}", EN_US)
        thing.reference_id = f"ref-{idx}"
        entities.append(thing)
    return entities


@pytest.mark.parametrize("suffix", [".ndjson", ".ndjson.gz"])
def test_round_trip_preserves_every_entity(tmp_path: Path, suffix: str) -> None:
    """Saving and loading must not drop entities — the file carries no header line."""
    target: Path = tmp_path / f"entities{suffix}"
    saved: List[ThingObject] = _things(3)

    save_import_format(target, saved)
    loaded: List[ThingObject] = load_import_format(target, raise_on_error=False)

    assert [thing.label[0].content for thing in loaded] == ["Person 0", "Person 1", "Person 2"]


@pytest.mark.parametrize("suffix", [".ndjson", ".ndjson.gz"])
def test_the_streaming_iterator_agrees_with_the_eager_loader(tmp_path: Path, suffix: str) -> None:
    """``iterate_large_import_format`` and ``load_import_format`` read the same file the same way."""
    target: Path = tmp_path / f"entities{suffix}"
    save_import_format(target, _things(3))

    streamed = [thing.label[0].content for thing in iterate_large_import_format(target)]
    eager = [thing.label[0].content for thing in load_import_format(target, raise_on_error=False)]

    assert streamed == eager


def test_saving_to_an_unsupported_suffix_is_reported(tmp_path: Path) -> None:
    """A suffix the writer does not understand must fail loudly, not write nothing."""
    target: Path = tmp_path / "entities.jsonl"

    with pytest.raises(ValueError):
        save_import_format(target, _things(1))


def test_the_ndjson_suffix_is_matched_case_insensitively(tmp_path: Path) -> None:
    """``.NDJSON`` is the same format as ``.ndjson``."""
    target: Path = tmp_path / "entities.NDJSON"

    save_import_format(target, _things(2))

    assert len(load_import_format(target, raise_on_error=False)) == 2
