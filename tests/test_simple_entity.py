# -*- coding: utf-8 -*-
# Copyright © 2023-present Wacom. All rights reserved.
import logging
import os
import uuid
from typing import List, Optional, Dict
from unittest import TestCase

import pytest
from faker import Faker

from knowledge.base.entity import Label
from knowledge.base.language import SUPPORTED_LOCALES, LocaleCode
from knowledge.base.ontology import (
    ThingObject,
    OntologyClassReference,
    OntologyPropertyReference,
    DataProperty,
    ObjectProperty,
)
from knowledge.services.graph import WacomKnowledgeService, Visibility, IndexType
from knowledge.services.ontology import OntologyService
from knowledge.services.users import UserManagementServiceAPI, User, UserRole
from knowledge.utils.graph import count_things

THING_OBJECT: OntologyClassReference = OntologyClassReference("wacom", "core", "Thing")


def create_thing() -> ThingObject:
    """
    Create a thing object with random data.
    Returns
    -------
    instance: ThingObject
        Thing object with random data.
    """
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse("wacom:core#Person"))
    for lang_inst in SUPPORTED_LOCALES:
        fake: Faker = Faker(lang_inst)
        name: str = fake.name()
        thing.add_label(name, lang_inst)
        thing.add_description(fake.text(), lang_inst)
        names: List[str] = name.split()
        if len(names) == 2:
            thing.add_data_property(
                DataProperty(names[0], OntologyPropertyReference.parse("wacom:core#firstName"), language_code=lang_inst)
            )
            thing.add_data_property(
                DataProperty(names[1], OntologyPropertyReference.parse("wacom:core#lastName"), language_code=lang_inst)
            )
        elif len(names) == 3:
            thing.add_data_property(
                DataProperty(names[1], OntologyPropertyReference.parse("wacom:core#firstName"), language_code=lang_inst)
            )
            thing.add_data_property(
                DataProperty(names[2], OntologyPropertyReference.parse("wacom:core#lastName"), language_code=lang_inst)
            )
    return thing


def create_page_thing() -> ThingObject:
    """
    Create a page thing object with random data.
    Returns
    -------
    instance: ThingObject
        Thing object with random data.
    """
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse("wacom:core#Page"))
    for lang_inst in SUPPORTED_LOCALES:
        fake: Faker = Faker(lang_inst)
        name: str = fake.name()
        thing.add_label(name, lang_inst)
        thing.add_description(fake.text(), lang_inst)
        thing.add_data_property(
            DataProperty(
                content=fake.text(), property_ref=OntologyPropertyReference.parse("wacom:core#content"),
                language_code=LocaleCode(lang_inst))
        )
    thing.use_full_text_index = False
    thing.use_vector_index = False
    thing.use_vector_index_document = False
    thing.use_for_nel = False
    return thing

@pytest.fixture(scope="class")
def cache_class(request):
    """
    Fixture to store data for the test cases.

    Parameters
    ----------
    request: pytest.FixtureRequest
        Request object.
    """

    class ClassDB:
        """
        Class to store data for the test cases.
        """

        def __init__(self):
            self.__external_id: Optional[str] = None
            self.__token: Optional[str] = None
            self.__thing_uri: Optional[str] = None

        @property
        def thing_uri(self) -> Optional[str]:
            return self.__thing_uri

        @thing_uri.setter
        def thing_uri(self, thing_uri: Optional[str]):
            self.__thing_uri = thing_uri

        @property
        def external_id(self) -> Optional[str]:
            return self.__external_id

        @external_id.setter
        def external_id(self, external_id: Optional[str]):
            self.__external_id = external_id

        @property
        def token(self) -> Optional[str]:
            return self.__token

        @token.setter
        def token(self, token: Optional[str]):
            self.__token = token

    # set a class attribute on the invoking test context
    request.cls.cache = ClassDB()


@pytest.mark.usefixtures("cache_class")
class EntityFlow(TestCase):
    """
    Testing the async client flows
    ------------------------------
    - Create user
    - Push entity
    - Get entity
    - Update entity
    - Pull literals from the entity
    - Pull labels from the entity
    - Pull relations from the entity
    - Delete entity
    """

    # -----------------------------------------------------------------------------------------------------------------
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Wacom Knowledge Listing", service_url=os.environ.get("INSTANCE"), service_endpoint="graph/v1"
    )
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(
        service_url=os.environ.get("INSTANCE"), service_endpoint="graph/v1"
    )
    ontology: OntologyService = OntologyService(service_url=os.environ.get("INSTANCE"), service_endpoint="ontology/v1")

    """User management service."""
    tenant_api_key: str = os.environ.get("TENANT_API_KEY")
    LIMIT: int = 10000

    def test_1_create_user(self):
        """Create user."""
        # Create an external user id
        self.cache.external_id = str(uuid.uuid4())
        # Create user
        _, token, refresh, expire = self.user_management.create_user(
            self.tenant_api_key,
            external_id=self.cache.external_id,
            meta_data={"account-type": "qa-test"},
            roles=[UserRole.USER],
        )
        self.cache.token = token

    def test_2_push_entity(self):
        """Push entity."""
        thing: ThingObject = create_thing()
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        uri_thing: str = self.knowledge_client.create_entity(thing)
        self.cache.thing_uri = uri_thing

    def test_3_get_entity(self):
        """Get entity."""
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        full_entity: ThingObject = self.knowledge_client.entity(self.cache.thing_uri)
        # Entities must not be empty
        self.assertIsNotNone(full_entity)

    def test_4_update_entity(self):
        """Update entity."""
        full_entity: ThingObject = self.knowledge_client.entity(self.cache.thing_uri)
        # Entities must not be empty
        self.assertIsNotNone(full_entity)

    def test_5_literal_entity(self):
        """Pull literals from the entity."""
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        literals: List[DataProperty] = self.knowledge_client.literals(self.cache.thing_uri)
        self.assertIsNotNone(literals)

    def test_6_labels_entity(self):
        """Pull labels from the entity."""
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        labels: List[Label] = self.knowledge_client.labels(self.cache.thing_uri)
        self.assertIsNotNone(labels)

    def test_7_relations_entity(self):
        """Pull relations from the entity."""
        # Pull relations if configured
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        relations: Dict[OntologyPropertyReference, ObjectProperty] = self.knowledge_client.relations(
            auth_key=self.cache.token, uri=self.cache.thing_uri
        )
        # Assert relations are
        self.assertIsNotNone(relations)
        self.assertEqual(len(relations), 0)

    def test_8_update_entity_indexes(self):
        """Test index operations."""
        index_thing: ThingObject = create_page_thing()
        entity_uri: str = self.knowledge_client.create_entity(index_thing)
        thing: ThingObject = self.knowledge_client.entity(entity_uri)
        self.assertFalse(thing.use_full_text_index)
        self.assertFalse(thing.use_vector_index)
        self.assertFalse(thing.use_vector_index_document)
        self.assertFalse(thing.use_for_nel)

        # Update ElasticSearch index and Remove NEL
        updates: Dict[IndexType, str] = self.knowledge_client.add_entity_indexes(entity_uri,
                                                                                 targets=["ElasticSearch"])
        self.assertEqual(updates["ElasticSearch"], "UPSERT")
        updates = self.knowledge_client.add_entity_indexes(entity_uri, targets=["ElasticSearch"])
        self.assertEqual(updates["ElasticSearch"], "Target already exists")
        thing = self.knowledge_client.entity(entity_uri)
        self.assertTrue(thing.use_full_text_index)
        self.assertFalse(thing.use_vector_index)
        self.assertFalse(thing.use_vector_index_document)
        self.assertFalse(thing.use_for_nel)
        # Update NEL index
        updates = self.knowledge_client.add_entity_indexes(entity_uri, targets=["NEL"])
        self.assertEqual(updates["NEL"], "UPSERT")
        thing = self.knowledge_client.entity(entity_uri)
        self.assertTrue(thing.use_full_text_index)
        self.assertFalse(thing.use_vector_index)
        self.assertFalse(thing.use_vector_index_document)
        self.assertTrue(thing.use_for_nel)
        # Update Vector index
        updates = self.knowledge_client.add_entity_indexes(entity_uri, targets=["VectorSearchWord",
                                                                                "VectorSearchDocument"])
        self.assertEqual(updates["VectorSearchWord"], "UPSERT")
        self.assertEqual(updates["VectorSearchDocument"], "UPSERT")
        thing = self.knowledge_client.entity(entity_uri)
        self.assertTrue(thing.use_full_text_index)
        self.assertTrue(thing.use_vector_index)
        self.assertTrue(thing.use_vector_index_document)
        self.assertTrue(thing.use_for_nel)
        # Remove all indexes
        updates = self.knowledge_client.remove_entity_indexes(entity_uri,
                                                              targets=["ElasticSearch", "NEL", "VectorSearchWord",
                                                                       "VectorSearchDocument"])
        self.assertEqual(updates["ElasticSearch"], "DELETE")
        self.assertEqual(updates["NEL"], "DELETE")
        self.assertEqual(updates["VectorSearchWord"], "DELETE")
        self.assertEqual(updates["VectorSearchDocument"], "DELETE")
        # Check if all indexes are removed
        thing = self.knowledge_client.entity(entity_uri)
        self.assertFalse(thing.use_full_text_index)
        self.assertFalse(thing.use_vector_index)
        self.assertFalse(thing.use_vector_index_document)
        self.assertFalse(thing.use_for_nel)



    def test_9_delete_entity(self):
        """Delete the entity."""
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        before_entities = count_things(
            self.knowledge_client, self.cache.token, THING_OBJECT, visibility=Visibility.PRIVATE
        )
        self.knowledge_client.delete_entity(self.cache.thing_uri, force=True)
        after_entities = count_things(
            self.knowledge_client, self.cache.token, THING_OBJECT, visibility=Visibility.PRIVATE
        )
        self.assertLess(after_entities, before_entities)

    def teardown_class(self):
        """Clean up the test environment."""
        list_user_all: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=EntityFlow.LIMIT)
        for u_i in list_user_all:
            if "account-type" in u_i.meta_data and u_i.meta_data.get("account-type") == "qa-test":
                logging.info(f"Clean user {u_i.external_user_id}")
                self.user_management.delete_user(
                    self.tenant_api_key, external_id=u_i.external_user_id, internal_id=u_i.id, force=True
                )
