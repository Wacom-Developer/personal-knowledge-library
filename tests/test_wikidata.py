# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from unittest import TestCase

import pytest

from knowledge.base.language import SUPPORTED_LOCALES, SUPPORTED_LANGUAGES, EN
from knowledge.base.ontology import OntologyPropertyReference, OntologyContext
from knowledge.ontomapping import register_ontology, load_configuration
from knowledge.ontomapping.manager import wikidata_to_thing
from knowledge.public.cache import WikidataCache
from knowledge.public.relations import wikidata_relations_extractor, wikidata_relations_extractor_qids
from knowledge.public.wikidata import WikidataThing, WikidataSearchResult, WikidataClass
from knowledge.public.client import WikiDataAPIClient
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.users import UserManagementServiceAPI, UserRole
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

        WIKIDATA_QIDS: List[str] = ["Q5582", "Q1028181", "Q19363211", ""]
        WIKIDATA_PIDS: List[str] = ["P31", "P279", "P361", "P170", "P50", "P170", "P19", "P20"]

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
    Test cases for Wikidata.
    --------------------------------
    1. Retrieve entities from Wikidata
    2. Extract relations between entities
    3. Convert Wikidata entities to Thing objects
    4. Check Wikipedia summary
    """

    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Wacom Knowledge Listing", service_url=os.environ.get("INSTANCE"), service_endpoint="graph/v1"
    )
    tenant_api_key: str = os.environ.get("TENANT_API_KEY")
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=os.environ.get("INSTANCE"))
    ontology_client: OntologyService = OntologyService(service_url=os.environ.get("INSTANCE"))
    external_id: Optional[str] = None

    def setUp(self):
        for user in self.user_management.listing_users(self.tenant_api_key):
            if UserRole.ADMIN in user.user_roles:
                self.external_id = user.external_user_id

        self.ontology_client.login(tenant_api_key=self.tenant_api_key, external_user_id=self.external_id)
        context: Optional[OntologyContext] = self.ontology_client.context()
        if not context:
            import sys

            sys.exit(0)
        else:
            context_name: str = context.context
            # Export ontology
            rdf_export: str = self.ontology_client.rdf_export(context_name)
            # Register ontology
            register_ontology(rdf_export)
            # Load configuration
            load_configuration(Path(__file__).parent.parent / "pkl-cache" / "ontology_mapping.json")

    def test_1_wikidata(self):
        """Test the retrieval of entities from Wikidata."""
        # Q762 is Leonardo da Vinci and Q12418 is Mona Lisa
        print("Retrieving entities from Wikidata...")
        entities: List[WikidataThing] = WikiDataAPIClient.retrieve_entities(["Q762", "Q12418"])
        self.assertEqual(len(entities), 2)
        self.cache.wikidata_things = dict([(e.qid, e) for e in entities])

    def test_2_relations(self):
        """Test relations."""
        # Extract relations between entities
        relations: Dict[str, List[Dict[str, Any]]] = wikidata_relations_extractor(self.cache.wikidata_things)
        self.assertGreaterEqual(len(relations), 2)
        self.cache.relations = relations

    def test_3_wikidata_to_thing(self):
        """Test the conversion of Wikidata entities to Thing objects. """
        for qid, wiki_thing in self.cache.wikidata_things.items():
            thing, warnings = wikidata_to_thing(
                wiki_thing, self.cache.relations, SUPPORTED_LOCALES, self.cache.wikidata_things
            )

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
        """Test Wikipedia function."""
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

    def test_5_wikidata_to_thing_conversion(self):
        """
        Test the conversion of Wikidata entities to Thing objects.
        """
        entities: List[WikidataThing] = WikiDataAPIClient.retrieve_entities(self.cache.WIKIDATA_QIDS)
        for e in entities:
            for l_locale in e.label_languages:
                self.assertIsNotNone(e.label_lang(l_locale))
            for a_locale in e.alias_languages:
                self.assertIsNotNone(e.alias_lang(a_locale))
            for d_locale in e.description_languages:
                self.assertIsNotNone(e.description_lang(d_locale))
            for w_cls in e.instance_of:
                self.assertIsInstance(w_cls, WikidataClass)
            dict_wikidata: Dict[str, Any] = e.__dict__()
            self.assertIsInstance(dict_wikidata, dict)

        wikidata_things: Dict[str, WikidataThing] = {e.qid: e for e in entities}
        relations: Dict[str, List[Dict[str, Any]]] = wikidata_relations_extractor(wikidata_things)
        relations_2: Dict[str, List[Dict[str, Any]]] = wikidata_relations_extractor_qids(
            wikidata_things, set(wikidata_things.keys())
        )
        for qid, rel in relations.items():
            if qid not in relations_2:
                self.fail(f"QID {qid} is not in the second relations.")
            if len(rel) != len(relations_2[qid]):
                self.fail(f"QID {qid} has different number of relations.")
        load_configuration(Path(__file__).parent.parent / "pkl-cache" / "ontology_mapping.json")
        van_gogh, import_warnings = wikidata_to_thing(
            wikidata_things["Q5582"],
            all_relations=relations,
            supported_locales=SUPPORTED_LOCALES,
            pull_wikipedia=True,
            all_wikidata_objects=wikidata_things,
        )
        check_lang: List[str] = []
        for la in van_gogh.label:
            if str(la.language_code) not in check_lang:
                check_lang.append(str(la.language_code))
            else:
                raise ValueError(f"There are more than one main label for {la.language_code}")
            if not la.main:
                raise ValueError(f"There is a label is not tagged as main. {la}")
        for al in van_gogh.alias:
            if str(al.language_code) not in check_lang:
                raise ValueError(
                    f"There is an alias with a language code {al.language_code} " f"that is not in the main labels."
                )

            if al.main:
                raise ValueError(f"Label is not alias. {al}")

    def test_6_search(self):
        """Test the search functionality."""
        search_results: List[WikidataSearchResult] = WikiDataAPIClient.search_term("Leonardo Da Vinci", EN)
        self.assertGreaterEqual(len(search_results), 1)
        qids: List[str] = [sr.qid for sr in search_results]
        if "Q762" not in qids:
            raise ValueError("Q762 (Leonardo Da Vinci) is not in the search results.")

    def test_7_taxonomy(self):
        """Test the taxonomy functionality."""
        taxonomy: Dict[str, WikidataClass] = WikiDataAPIClient.superclasses("Q5")
        self.assertGreaterEqual(len(taxonomy), 1)
        for cls in taxonomy.values():
            self.assertIsInstance(cls, WikidataClass)
            self.assertIsInstance(cls.qid, str)
            self.assertIsInstance(cls.label, str)
            self.assertIsInstance(cls.__dict__(), dict)
        subclasses: Dict[str, WikidataClass] = WikiDataAPIClient.subclasses("Q5")
        self.assertGreaterEqual(len(subclasses), 1)
        for cls in subclasses.values():
            self.assertIsInstance(cls, WikidataClass)
            self.assertIsInstance(cls.qid, str)
            self.assertIsInstance(cls.label, str)
            self.assertIsInstance(cls.__dict__(), dict)

    def test_8_check_test(self):
        """Test the cache functionality."""
        cache: WikidataCache = WikidataCache()
        cache.load_cache(Path(__file__).parent.parent / "pkl-cache")
        self.assertGreater(cache.number_of_cached_objects(), 0)
        self.assertGreater(cache.number_of_cached_properties(), 0)
        for pid in self.cache.WIKIDATA_PIDS:
            prop = cache.property_in_cache(pid)
            print(prop)



