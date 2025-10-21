# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom. All rights reserved.
import os
import uuid
from typing import Optional, List
from unittest import TestCase

import pytest
from faker import Faker

from knowledge.base.entity import Label, LABELS_TAG, INDEXING_NEL_TARGET
from knowledge.base.language import EN_US, SUPPORTED_LOCALES
from knowledge.base.ontology import (
    OntologyClassReference,
    ThingObject,
    DataProperty,
    OntologyPropertyReference,
    SYSTEM_SOURCE_REFERENCE_ID,
    ObjectProperty,
    SYSTEM_SOURCE_SYSTEM,
)
from knowledge.base.response import JobStatus, NewEntityUrisResponse
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.users import UserRole, UserManagementServiceAPI, User

THING_OBJECT: OntologyClassReference = OntologyClassReference("wacom", "core", "Thing")
LINKS: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#links")


@pytest.fixture(scope="class")
def cache_class(request):
    class ClassDB:
        """
        Class to store data for the test cases.
        """

        def __init__(self):
            self.__external_id: Optional[str] = None
            self.__token: Optional[str] = None

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

    # set a class attribute on the invoking test context
    request.cls.cache = ClassDB()


def create_random_thing(reference_id: str, uri: str) -> ThingObject:
    """
    Create a random thing object with random data.
    Parameters
    ----------
    reference_id: str
        Reference id of the thing object.
    uri: str
        URI of the thing object.

    Returns
    -------
    random_thing: ThingObject
        Thing object with random data.
    """
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse("wacom:core#Topic"))
    for lang_inst in SUPPORTED_LOCALES:
        fake: Faker = Faker(lang_inst)
        name: str = fake.name()
        thing.add_label(name, lang_inst)
        thing.add_description(fake.text(), lang_inst)
    thing.add_data_property(DataProperty(reference_id, SYSTEM_SOURCE_REFERENCE_ID, language_code=EN_US))
    thing.add_data_property(DataProperty("test-case", SYSTEM_SOURCE_SYSTEM, language_code=EN_US))
    thing.add_relation(ObjectProperty(relation=LINKS, outgoing=[uri]))
    return thing


@pytest.mark.usefixtures("cache_class")
class ImportFlow(TestCase):
    """
    Import Flow
    ----------
    Test the import format flow
    """

    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Wacom Knowledge Listing", service_url=os.environ.get("INSTANCE"), service_endpoint="graph/v1"
    )
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(
        service_url=os.environ.get("INSTANCE"), service_endpoint="graph/v1"
    )
    tenant_api_key: str = os.environ.get("TENANT_API_KEY")
    LIMIT: int = 1000

    def test_1_create_user(self):
        """Create user."""
        # Create an external user id
        self.cache.external_id = str(uuid.uuid4())
        # Create user
        _, token, refresh, expire = self.user_management.create_user(
            self.tenant_api_key,
            external_id=self.cache.external_id,
            meta_data={"account-type": "qa-test"},
            roles=[UserRole.CONTENT_MANAGER],
        )
        self.cache.token = token

    def test_2_import_use_nel(self):
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

    def test_3_labels_import(self):
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

    def test_4_import_test(self):
        """
        Test Import
        """
        entity: ThingObject = ThingObject(
            label=[Label(content="Test", language_code=EN_US, main=True)], concept_type=THING_OBJECT, use_for_nel=True
        )
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        uri_thing: str = self.knowledge_client.create_entity(entity)
        things: List[ThingObject] = [create_random_thing(f"ref-{i}", uri_thing) for i in range(10)]
        job_id: str = self.knowledge_client.import_entities(things)
        new_uris: List[str] = []
        while True:
            job_status: JobStatus = self.knowledge_client.job_status(job_id)
            if job_status.status == JobStatus.COMPLETED:
                break
        next_page_id = None
        while True:
            resp: NewEntityUrisResponse = self.knowledge_client.import_new_uris(job_id, next_page_id=next_page_id)
            new_uris.extend(resp.new_entities_uris)
            if resp.next_page_id is None:
                break
            next_page_id = resp.next_page_id

        errors = self.knowledge_client.import_error_log(job_id)

        if len(new_uris) == 0:
            raise Exception(f"Import failed with errors: {errors}")
        for uri in new_uris:
            thing: ThingObject = self.knowledge_client.entity(uri)
            thing.object_properties = self.knowledge_client.relations(uri)
            self.assertIsNotNone(thing)
            self.assertEqual(thing.use_for_nel, True)
            self.assertTrue(LINKS in thing.object_properties)
            self.assertEqual(thing.object_properties[LINKS].outgoing_relations[0].uri, uri_thing)

    def teardown_class(self):
        """Delete the entity."""
        """Clean up the test environment."""
        list_user_all: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=ImportFlow.LIMIT)
        for u_i in list_user_all:
            if "account-type" in u_i.meta_data and u_i.meta_data.get("account-type") == "qa-test":
                try:
                    self.user_management.delete_user(
                        self.tenant_api_key, external_id=u_i.external_user_id, internal_id=u_i.id, force=True
                    )
                except Exception as e:
                    print(f"Error deleting user {u_i.external_user_id}: {e}")
