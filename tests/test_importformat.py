# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom. All rights reserved.
from unittest import TestCase

from faker import Faker

from knowledge.base.entity import Label, LABELS_TAG, INDEXING_NEL_TARGET
from knowledge.base.language import EN_US, SUPPORTED_LOCALES
from knowledge.base.ontology import OntologyClassReference, ThingObject

THING_OBJECT: OntologyClassReference = OntologyClassReference("wacom", "core", "Thing")


class ImportFlow(TestCase):
    """
    Import Flow
    ----------
    Test the import format flow
    """

    def test_import_use_nel(self):
        """
        Test Import Use Nel.
        """
        faker: Faker = Faker(EN_US)
        entity: ThingObject = ThingObject(
            label=[Label(content=faker.word(), language_code=EN_US, main=True)],
            concept_type=THING_OBJECT,
            use_for_nel=True,
        )

        entity_dict = entity.__import_format_dict__()
        self.assertTrue(INDEXING_NEL_TARGET in entity_dict["targets"])
        new_entity = ThingObject.from_import_dict(entity_dict)
        self.assertEqual(new_entity.use_for_nel, entity.use_for_nel)

    def test_labels_import(self):
        """
        Test Labels Import
        """
        entity: ThingObject = ThingObject()
        for locale in SUPPORTED_LOCALES:
            faker: Faker = Faker(locale)
            entity.add_label(label=faker.word(), language_code=locale)
            for _ in range(3):
                entity.add_alias(alias=faker.word(), language_code=locale)
        entity_dict = entity.__import_format_dict__()
        self.assertEqual(len(entity_dict[LABELS_TAG]), len(entity.label) + len(entity.alias))
        new_entity = ThingObject.from_import_dict(entity_dict)
        self.assertEqual(len(new_entity.label), len(entity.label))
        self.assertEqual(len(new_entity.alias), len(entity.alias))
