# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the locale lookups on ``ThingObject``.

``label_lang`` / ``description_lang`` / ``alias_lang`` are typed
``Union[LocaleCode, LanguageCode]``, so both ``EN_US`` (``"en_US"``) and the bare ``EN``
(``"en"``) are valid arguments. A bare language code must resolve to the labels of that
language rather than silently matching nothing. No server required.
"""

from typing import List

import pytest

from knowledge.base.language import DE, DE_DE, EN, EN_US, JA, JA_JP, LocaleCode
from knowledge.base.ontology import OntologyClassReference, ThingObject

PERSON: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")


@pytest.fixture()
def thing() -> ThingObject:
    entity: ThingObject = ThingObject(concept_type=PERSON)
    entity.add_label("Leonardo da Vinci", EN_US)
    entity.add_label("Leonardo da Vinci", DE_DE)
    entity.add_label("レオナルド・ダ・ヴィンチ", JA_JP)
    entity.add_alias("Leonardo", EN_US)
    entity.add_alias("Da Vinci", EN_US)
    entity.add_description("Renaissance polymath", EN_US)
    entity.add_description("Renaissance-Universalgelehrter", DE_DE)
    return entity


# --------------------------------------------- locale codes -----------------------------------------------------------
def test_a_locale_code_resolves_its_label(thing: ThingObject) -> None:
    """Baseline: an exact locale match still works."""
    label = thing.label_lang(EN_US)

    assert label is not None
    assert label.content == "Leonardo da Vinci"


def test_a_locale_code_resolves_its_description(thing: ThingObject) -> None:
    """Baseline: an exact locale match still works."""
    description = thing.description_lang(DE_DE)

    assert description is not None
    assert description.content == "Renaissance-Universalgelehrter"


def test_a_locale_code_resolves_its_aliases(thing: ThingObject) -> None:
    """Baseline: an exact locale match still works."""
    assert [alias.content for alias in thing.alias_lang(EN_US)] == ["Leonardo", "Da Vinci"]


def test_an_absent_locale_resolves_to_nothing(thing: ThingObject) -> None:
    """A locale the entity has no label for is still a miss."""
    assert thing.label_lang(LocaleCode("fr_FR")) is None
    assert thing.description_lang(LocaleCode("fr_FR")) is None
    assert thing.alias_lang(LocaleCode("fr_FR")) == []


# -------------------------------------------- language codes ----------------------------------------------------------
def test_a_bare_language_code_resolves_a_label(thing: ThingObject) -> None:
    """``EN`` must find the ``en_US`` label — the signature accepts a LanguageCode."""
    label = thing.label_lang(EN)

    assert label is not None
    assert label.content == "Leonardo da Vinci"


def test_a_bare_language_code_resolves_a_description(thing: ThingObject) -> None:
    """``DE`` must find the ``de_DE`` description."""
    description = thing.description_lang(DE)

    assert description is not None
    assert description.content == "Renaissance-Universalgelehrter"


def test_a_bare_language_code_resolves_aliases(thing: ThingObject) -> None:
    """``EN`` must find the ``en_US`` aliases."""
    assert [alias.content for alias in thing.alias_lang(EN)] == ["Leonardo", "Da Vinci"]


def test_a_bare_language_code_for_a_non_latin_locale_resolves(thing: ThingObject) -> None:
    """The prefix match is not limited to Latin-script locales."""
    label = thing.label_lang(JA)

    assert label is not None
    assert label.content == "レオナルド・ダ・ヴィンチ"


def test_a_bare_language_code_the_entity_lacks_resolves_to_nothing(thing: ThingObject) -> None:
    """A language with no labels at all is still a miss."""
    assert thing.label_lang(EN.__class__("fr")) is None


def test_a_language_code_does_not_match_a_different_language(thing: ThingObject) -> None:
    """``de`` must not be satisfied by an ``en_US`` label."""
    labels: List[str] = []
    label = thing.label_lang(DE)
    if label is not None:
        labels.append(label.content)

    assert thing.label_lang(DE) is not None
    assert thing.description_lang(JA) is None, "ja has a label but no description"
