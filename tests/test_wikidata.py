# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import os
from typing import List, Dict, Any, Optional
from unittest import TestCase

import pytest

from knowledge.base.ontology import SUPPORTED_LOCALES, ThingObject, OntologyPropertyReference, SUPPORTED_LANGUAGES, \
    OntologyContext
from knowledge.ontomapping import register_ontology, load_configuration, get_mapping_configuration
from knowledge.ontomapping.manager import wikidata_to_thing
from knowledge.public.relations import wikidata_relations_extractor
from knowledge.public.wikidata import WikidataThing, WikiDataAPIClient
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.users import UserManagementServiceAPI
from knowledge.utils.wikipedia import get_wikipedia_summary, get_wikipedia_summary_image

# Configuration
PERSON: str = "wacom:core#Person"
VISUAL_ARTWORK: str = "wacom:creative#VisualArtwork"
IS_CREATED: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#isCreatedBy")
CREATED: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#created")
HAS_NOTEABLE_WORK: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#hasNotableWork")
LAST_NAME: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#lastName")
FIRST_NAME: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#firstName")
GENDER: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#gender")
DATE_OF_DEATH: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#dateOfDeath")
DATE_OF_BIRTH: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#dateOfBirth")
WEBSITE: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#website")
INCEPTION: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:education#inception")
COORDINATE_LOCATION: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:geography#coordinateLocation")


@pytest.fixture(scope="class")
def cache_class(request):
    class ClassDB:
        """
        Class to store data for the test cases.
        """

        def __init__(self):
            self.__wikidata_things: dict[str, WikidataThing] = {}
            self.__relations: dict[str, dict[str, Any]] = {}

        @property
        def wikidata_things(self) -> dict[str, WikidataThing]:
            return self.__wikidata_things

        @wikidata_things.setter
        def wikidata_things(self, wikidata_things: dict[str, WikidataThing]):
            self.__wikidata_things = wikidata_things

        @property
        def relations(self) -> dict[str, dict[str, Any]]:
            return self.__relations

        @relations.setter
        def relations(self, relations: dict[str, dict[str, Any]]):
            self.__relations = relations

    # set a class attribute on the invoking test context
    request.cls.cache = ClassDB()


@pytest.mark.usefixtures("cache_class")
class WikidataFlow(TestCase):
    """
    Test cases for Wikidata.
    --------------------------------
    1. Retrieve entities from Wikidata
    2. Extract relations between entities
    3. Convert Wikidata entities to Thing objects
    4. Check Wikipedia summary
    """

    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Wacom Knowledge Listing",
                                                                    service_url=os.environ.get('INSTANCE'),
                                                                    service_endpoint="graph/v1")
    tenant_api_key: str = os.environ.get('TENANT_API_KEY')
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=os.environ.get('INSTANCE'))
    ontology_client: OntologyService = OntologyService(service_url=os.environ.get('INSTANCE'))
    external_id: str = os.environ.get('ADMIN_EXTERNAL_ID')

    def setUp(self):

        admin_token, refresh, expire = self.knowledge_client.request_user_token(self.tenant_api_key, self.external_id)
        context: Optional[OntologyContext] = self.ontology_client.context(admin_token)
        if not context:
            import sys
            sys.exit(0)
        else:
            context_name: str = context.context
            # Export ontology
            rdf_export: str = self.ontology_client.rdf_export(admin_token, context_name)
            # Register ontology
            register_ontology(rdf_export)
            # Load configuration
            load_configuration()

    def test_1_wikidata(self):
        # Q762 is Leonardo da Vinci and Q12418 is Mona Lisa
        entities: list[WikidataThing] = WikiDataAPIClient.retrieve_entities(["Q762", "Q12418"])
        self.assertEqual(len(entities), 2)
        self.cache.wikidata_things = dict([(e.qid, e) for e in entities])

    def test_2_relations(self):
        # Extract relations between entities
        relations: dict[str, list[dict[str, Any]]] = wikidata_relations_extractor(self.cache.wikidata_things)
        self.assertGreaterEqual(len(relations), 2)
        self.cache.relations = relations

    def test_3_wikidata_to_thing(self):
        for qid, wiki_thing in self.cache.wikidata_things.items():
            thing, warnings = wikidata_to_thing(wiki_thing, self.cache.relations, SUPPORTED_LOCALES,
                                                self.cache.wikidata_things)

            if qid == "Q762":
                # Leonardo da Vinci
                self.assertEqual(thing.concept_type.iri, PERSON)
                self.assertTrue(HAS_NOTEABLE_WORK in thing.object_properties or CREATED in thing.object_properties)
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
                self.assertEqual(len(thing.object_properties), 0)

    def test_4_check_wikipedia(self):
        for qid, wiki_thing in self.cache.wikidata_things.items():
            for source, item in wiki_thing.sitelinks.items():
                if source == "wiki":
                    print(item)
                    for lang, title in item.titles.items():
                        if lang in SUPPORTED_LANGUAGES:
                            # Get summary
                            summary: str = get_wikipedia_summary(title=title, lang=lang)
                            self.assertIsNotNone(summary)
                            # Get image
                            image_url = get_wikipedia_summary_image(title=title, lang=lang)
                            self.assertIsNotNone(image_url)


