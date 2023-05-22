# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
from typing import List, Dict, Any
from unittest import TestCase

import pytest

from knowledge.base.ontology import SUPPORTED_LOCALES, ThingObject, OntologyPropertyReference, SUPPORTED_LANGUAGES
from knowledge.ontomapping.manager import wikidata_to_thing
from knowledge.public.relations import wikidata_relations_extractor
from knowledge.public.wikidata import WikidataThing, WikiDataAPIClient
from knowledge.utils.wikipedia import get_wikipedia_summary, get_wikipedia_summary_image

# Configuration
PERSON: str = "wacom:core#Person"
VISUAL_ARTWORK: str = "wacom:creative#VisualArtwork"
IS_CREATED: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#isCreatedBy")
HAS_NOTEABLE_WORK: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#hasNotableWork")
LAST_NAME: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#lastName")
FIRST_NAME: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#firstName")
GENDER: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#gender")
DATE_OF_DEATH: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#dateOfDeath")
DATE_OF_BIRTH: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#dateOfBirth")
WEBSITE: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#website")
INCEPTION: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#inception")
COORDINATE_LOCATION: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:geography#coordinateLocation")


@pytest.fixture(scope="class")
def cache_class(request):
    class ClassDB:
        """
        Class to store data for the test cases.
        """

        def __init__(self):
            self.__wikidata_things: Dict[str, WikidataThing] = {}
            self.__relations: Dict[str, Dict[str, Any]] = {}

        @property
        def wikidata_things(self) -> Dict[str, WikidataThing]:
            return self.__wikidata_things

        @wikidata_things.setter
        def wikidata_things(self, wikidata_things: Dict[str, WikidataThing]):
            self.__wikidata_things = wikidata_things

        @property
        def relations(self) -> Dict[str, Dict[str, Any]]:
            return self.__relations

        @relations.setter
        def relations(self, relations: Dict[str, Dict[str, Any]]):
            self.__relations = relations

    # set a class attribute on the invoking test context
    request.cls.cache = ClassDB()


@pytest.mark.usefixtures("cache_class")
class WikidataFlow(TestCase):
    """
    Testing the entity flow
    ---------------------
    - Create entity

    """

    def test_1_wikidata(self):
        # Q762 is Leonardo da Vinci and Q12418 is Mona Lisa
        entities: List[WikidataThing] = WikiDataAPIClient.retrieve_entities(["Q762", "Q12418"])
        self.assertEqual(len(entities), 2)
        self.cache.wikidata_things = dict([(e.qid, e) for e in entities])

    def test_2_relations(self):
        # Extract relations between entities
        relations: Dict[str, List[Dict[str, Any]]] = wikidata_relations_extractor(self.cache.wikidata_things)
        self.assertGreaterEqual(len(relations), 2)
        self.cache.relations = relations

    def test_3_wikidata_to_thing(self):
        for qid, wiki_thing in self.cache.wikidata_things.items():
            thing: ThingObject = wikidata_to_thing(wiki_thing, self.cache.relations, SUPPORTED_LOCALES)
            print(thing.object_properties.keys())
            print(thing.data_properties.keys())

            if qid == "Q762":
                # Leonardo da Vinci
                self.assertEqual(thing.concept_type.iri, PERSON)
                self.assertTrue(HAS_NOTEABLE_WORK in thing.object_properties)
                self.assertTrue(WEBSITE in thing.data_properties)
                self.assertTrue(DATE_OF_BIRTH in thing.data_properties)
                self.assertTrue(DATE_OF_DEATH in thing.data_properties)
                self.assertTrue(GENDER in thing.data_properties)
                self.assertTrue(FIRST_NAME in thing.data_properties)
                self.assertTrue(LAST_NAME in thing.data_properties)
                self.assertEqual(len(thing.object_properties), 1)
            elif qid == "Q12418":
                # Mona Lisa
                self.assertEqual(thing.concept_type.iri, VISUAL_ARTWORK)
                self.assertTrue(INCEPTION in thing.data_properties)
                self.assertTrue(COORDINATE_LOCATION in thing.data_properties)
                self.assertEqual(len(thing.object_properties), 1)

    def test_4_check_wikipedia(self):
        for qid, wiki_thing in self.cache.wikidata_things.items():
            for source, item in wiki_thing.sitelinks.items():
                if source == "wiki":
                    for lang, title in item.titles.items():
                        if lang in SUPPORTED_LANGUAGES:
                            # Get summary
                            summary: str = get_wikipedia_summary(title=title, lang=lang)
                            self.assertIsNotNone(summary)
                            # Get image
                            image_url = get_wikipedia_summary_image(title=title, lang=lang)
                            self.assertIsNotNone(image_url)


