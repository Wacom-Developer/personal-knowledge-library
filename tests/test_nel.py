# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import logging
import os
import uuid
from typing import List, Optional, Dict, Tuple, Any
from unittest import TestCase

import pytest
from faker import Faker
from knowledge.nel.base import KnowledgeGraphEntity

from knowledge.services.base import WacomServiceException

from knowledge.nel.engine import WacomEntityLinkingEngine
from ontospy import Ontospy, OntoClass, OntoProperty

from knowledge.base.entity import LanguageCode
from knowledge.base.ontology import ThingObject, OntologyClassReference, OntologyPropertyReference, DataProperty
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.users import UserManagementServiceAPI, User, UserRole


THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')


def random_value(data_type: str, faker_inst: Faker) -> Any:
    """
    Create a random value for a property.
    Parameters
    ----------
    data_type: str
        Data type of the property.
    faker_inst: Faker
        Faker instance.

    Returns
    -------
    value: Any
        Random value.
    """
    if data_type == 'http://www.w3.org/2001/XMLSchema#string':
        return faker_inst.catch_phrase()
    elif data_type == 'http://www.w3.org/2001/XMLSchema#dateTime':
        return faker_inst.date_time_this_year().isoformat()
    elif data_type == 'http://www.w3.org/2001/XMLSchema#date':
        return faker_inst.date_this_year().isoformat()
    elif data_type == 'http://www.w3.org/2001/XMLSchema#anyURI':
        return faker_inst.url()
    elif data_type == 'http://www.w3.org/2001/XMLSchema#integer':
        return faker_inst.random_int(min=-100, max=100)
    elif data_type == 'http://www.w3.org/2001/XMLSchema#decimal':
        return float(faker_inst.pydecimal(min_value=-1000., max_value=1000.))
    return None


def create_thing(class_ref: OntoClass) -> tuple[ThingObject, dict[OntologyPropertyReference,
                                                                  list[OntologyClassReference]]]:
    """
    Create a thing object with random data.
    Parameters
    ----------
    class_ref: OntoClass
        OntoClass instance.

    Returns
    -------
    instance: ThingObject
        Thing object with random data.
    mapping: dict[OntologyPropertyReference, list[OntologyClassReference]]
        Mapping of properties to classes.
    """
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse(class_ref.uri))
    relations: dict[OntologyPropertyReference, list[OntologyClassReference]] = {}
    for lang in ['ja_JP', 'en_US', 'de_DE', 'bg_BG', 'fr_FR', 'it_IT', 'es_ES', 'ru_RU']:
        fake: Faker = Faker(lang)
        thing.add_label(fake.name(), LanguageCode(lang))
        thing.add_description(fake.text(), LanguageCode(lang))
        if len(class_ref.domain_of_inferred) > 2:
            for props in class_ref.domain_of_inferred[1].values():
                for prop in props:
                    onto_prop: OntoProperty = prop
                    if str(onto_prop.uri) in ['wacom:core#description']:
                        continue
                    if str(onto_prop.rdftype) == 'http://www.w3.org/2002/07/owl#ObjectProperty':
                        relations[OntologyPropertyReference.parse(onto_prop.uri)] = \
                            [OntologyClassReference.parse(str(e.uri)) for e in prop.ranges]
                    else:
                        prop_ref: OntologyPropertyReference = OntologyPropertyReference.parse(onto_prop.uri)
                        content: Any = random_value(str(prop.ranges[0].uri), fake)
                        thing.add_data_property(DataProperty(content, property_ref=prop_ref,
                                                             language_code=LanguageCode(lang)))

    return thing, relations


@pytest.fixture(scope="class")
def cache_class(request):
    class ClassDB:
        """
        Class to store data for the test cases.
        """

        def __init__(self):
            self.__external_id: Optional[str] = None
            self.__token: Optional[str] = None
            self.__model: Optional[Ontospy] = None

        @property
        def external_id(self) -> Optional[str]:
            """External user id."""
            return self.__external_id

        @external_id.setter
        def external_id(self, external_id: Optional[str]):
            self.__external_id = external_id

        @property
        def token(self) -> Optional[str]:
            """User token."""
            return self.__token

        @token.setter
        def token(self, token: Optional[str]):
            self.__token = token

        @property
        def model(self) -> Optional[Ontospy]:
            """ Ontology model."""
            return self.__model

        @model.setter
        def model(self, model: Optional[Ontospy]):
            self.__model = model

    # set a class attribute on the invoking test context
    request.cls.cache = ClassDB()


@pytest.mark.usefixtures("cache_class")
class EntityFlow(TestCase):
    """
    Testing the entity flow
    ---------------------
    - Create entity

    """
    # -----------------------------------------------------------------------------------------------------------------
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Wacom Knowledge Listing",
                                                                    service_url=os.environ.get('INSTANCE'))
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=os.environ.get('INSTANCE'))
    ontology: OntologyService = OntologyService(service_url=os.environ.get('INSTANCE'))
    #  Wacom Named Entity Linking
    nel_client: WacomEntityLinkingEngine = WacomEntityLinkingEngine(
        service_url=os.environ.get('INSTANCE'),
        service_endpoint=WacomEntityLinkingEngine.SERVICE_ENDPOINT
    )

    '''User management service.'''
    tenant_api_key: str = os.environ.get('TENANT_API_KEY')
    LIMIT: int = 10000

    def test_1_create_user(self):
        """ Create a user. """
        # Create an external user id
        self.cache.external_id = str(uuid.uuid4())
        # Create user
        _, token, refresh, expire = self.user_management.create_user(self.tenant_api_key,
                                                                     external_id=self.cache.external_id,
                                                                     meta_data={'account-type': 'qa-test'},
                                                                     roles=[UserRole.USER])
        self.cache.token = token

    def test_2_nel_en(self):
        """ Test the named entity linking for English."""
        en_us: LanguageCode = LanguageCode('en_US')
        entities, _, _ = self.knowledge_client.listing(self.cache.token, THING_OBJECT, page_id=None, limit=10,
                                                       locale=en_us)
        fake: Faker = Faker(en_us)
        for ent in entities:
            if ent.use_for_nel:
                text: str = f'{fake.text()} Do not forget about {entities[0].label_lang(en_us).content}.'
                self.assertTrue(self.nel_client.is_language_supported(en_us))
                linked_entities: list[KnowledgeGraphEntity] = self.nel_client.link_personal_entities(self.cache.token,
                                                                                                     text=text)
                self.assertGreaterEqual(len(linked_entities), 1)

    def test_3_nel_ja(self):
        """ Test the named entity linking for Japanese."""
        ja_jp: LanguageCode = LanguageCode('ja_JP')
        entities, _, _ = self.knowledge_client.listing(self.cache.token, THING_OBJECT, page_id=None, limit=10,
                                                       locale=ja_jp)
        fake: Faker = Faker(ja_jp)
        for ent in entities:
            if ent.use_for_nel:
                text: str = f'{fake.text()}{entities[0].label_lang(ja_jp).content}'
                self.assertTrue(self.nel_client.is_language_supported(ja_jp))
                linked_entities: list[KnowledgeGraphEntity] = self.nel_client.\
                    link_personal_entities(self.cache.token, text=text, language_code=ja_jp)
                self.assertGreaterEqual(len(linked_entities), 1)

    def test_4_nel_de(self):
        """ Test the named entity linking for German."""
        de_de: LanguageCode = LanguageCode('de_DE')
        entities, _, _ = self.knowledge_client.listing(self.cache.token, THING_OBJECT, page_id=None, limit=10,
                                                       locale=de_de)
        fake: Faker = Faker(de_de)
        for ent in entities:
            if ent.use_for_nel:
                text: str = f'{fake.text()}. {entities[0].label_lang(de_de).content}.'
                self.assertTrue(self.nel_client.is_language_supported(de_de))
                linked_entities: list[KnowledgeGraphEntity] = self.nel_client.link_personal_entities(self.cache.token,
                                                                                                     text=text)
                self.assertGreaterEqual(len(linked_entities), 1)

    def teardown_class(self):
        """ Clean up the test environment. """
        list_user_all: list[User] = self.user_management.listing_users(self.tenant_api_key, limit=EntityFlow.LIMIT)
        for u_i in list_user_all:
            if 'account-type' in u_i.meta_data and u_i.meta_data.get('account-type') == 'qa-test':
                logging.info(f'Clean user {u_i.external_user_id}')
                try:
                    self.user_management.delete_user(self.tenant_api_key,
                                                     external_id=u_i.external_user_id, internal_id=u_i.id)
                except WacomServiceException as we:
                    logging.error(f'Error during user deletion: {we}')
