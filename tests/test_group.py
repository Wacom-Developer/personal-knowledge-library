# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import logging
import os
import uuid
from pathlib import Path
from typing import List, Optional
from unittest import TestCase

import pytest
from faker import Faker

from knowledge.base.entity import LanguageCode
from knowledge.base.ontology import ThingObject, OntologyClassReference
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.group import GroupManagementServiceAPI, Group
from knowledge.services.ontology import OntologyService
from knowledge.services.users import UserManagementServiceAPI, User, UserRole

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')


def create_thing() -> ThingObject:
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse('wacom:core#Person'))
    for lang in ['ja_JP', 'en_US', 'de_DE']:
        fake: Faker = Faker(lang)
        name: str = fake.name()
        lang_inst: LanguageCode = LanguageCode(lang)
        thing.add_label(name, lang_inst)
        thing.add_description(fake.text(), lang_inst)
    return thing


@pytest.fixture(scope="class")
def cache_class(request):
    class ClassDB:
        """
        Class to store data for the test cases.
        """

        def __init__(self):
            self.__group_id: Optional[str] = None
            self.__external_id: Optional[str] = None
            self.__external_id_2: Optional[str] = None
            self.__internal_id_2: Optional[str] = None
            self.__token: Optional[str] = None
            self.__token_2: Optional[str] = None
            self.__thing_uri: Optional[str] = None
            self.__join_key: Optional[str] = None

        @property
        def thing_uri(self) -> Optional[str]:
            return self.__thing_uri

        @thing_uri.setter
        def thing_uri(self, thing_uri: Optional[str]):
            self.__thing_uri = thing_uri

        @property
        def group_id(self) -> Optional[str]:
            return self.__group_id

        @group_id.setter
        def group_id(self, group_id: Optional[str]):
            self.__group_id = group_id

        @property
        def join_key(self) -> Optional[str]:
            return self.__join_key

        @join_key.setter
        def join_key(self, join_key: Optional[str]):
            self.__join_key = join_key

        @property
        def external_id(self) -> Optional[str]:
            return self.__external_id

        @external_id.setter
        def external_id(self, external_id: Optional[str]):
            self.__external_id = external_id

        @property
        def external_id_2(self) -> Optional[str]:
            return self.__external_id_2

        @external_id_2.setter
        def external_id_2(self, external_id: Optional[str]):
            self.__external_id_2 = external_id

        @property
        def internal_id_2(self) -> Optional[str]:
            return self.__internal_id_2

        @internal_id_2.setter
        def internal_id_2(self, internal_id: Optional[str]):
            self.__internal_id_2 = internal_id

        @property
        def token(self) -> Optional[str]:
            return self.__token

        @token.setter
        def token(self, token: Optional[str]):
            self.__token = token

        @property
        def token_2(self) -> Optional[str]:
            return self.__token_2

        @token_2.setter
        def token_2(self, token: Optional[str]):
            self.__token_2 = token

    # set a class attribute on the invoking test context
    request.cls.cache = ClassDB()


@pytest.mark.usefixtures("cache_class")
class GroupFlow(TestCase):
    """
    Testing the group flow
    ---------------------
    - Create entity
    - Share entity
    - Access

    """
    # -----------------------------------------------------------------------------------------------------------------
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Wacom Knowledge Listing",
                                                                    service_url=os.environ.get('INSTANCE'))
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=os.environ.get('INSTANCE'))
    ontology: OntologyService = OntologyService(service_url=os.environ.get('INSTANCE'))
    group_management: GroupManagementServiceAPI = GroupManagementServiceAPI(service_url=os.environ.get('INSTANCE'))

    '''User management service.'''
    tenant_api_key: str = os.environ.get('TENANT_API_KEY')
    LIMIT: int = 10000

    def test_1_create_users(self):
        """ Create users."""
        # Create an external user id
        self.cache.external_id = str(uuid.uuid4())
        self.cache.external_id_2 = str(uuid.uuid4())

        # Create user
        _, token, refresh, expire = self.user_management.create_user(self.tenant_api_key,
                                                                     external_id=self.cache.external_id,
                                                                     meta_data={'account-type': 'qa-test'},
                                                                     roles=[UserRole.USER])
        self.cache.token = token
        info, token, refresh, expire = self.user_management.create_user(self.tenant_api_key,
                                                                        external_id=self.cache.external_id_2,
                                                                        meta_data={'account-type': 'qa-test'},
                                                                        roles=[UserRole.USER])
        self.cache.token_2 = token
        self.cache.internal_id_2 = info.id

    def test_2_push_entity(self):
        """ Push entity."""
        thing: ThingObject = create_thing()
        uri_thing: str = self.knowledge_client.create_entity(self.cache.token, thing)
        self.cache.thing_uri = uri_thing
        self.knowledge_client.set_entity_image_local(self.cache.token, uri_thing,
                                                     Path(__file__).parent / '..' / 'assets' / 'dummy.png')

    def test_3_create_group(self):
        """ Create group."""
        # Now, user 1 creates a group
        g: Group = self.group_management.create_group(self.cache.token, "qa-test-group")
        self.cache.group_id = g.id
        self.cache.join_key = g.join_key

    def test_4_join_group(self):
        """ Join group."""
        self.knowledge_client.entity(self.cache.token, self.cache.thing_uri)
        try:
            self.knowledge_client.entity(self.cache.token_2, self.cache.thing_uri)
            self.fail("User 2 should not have access to the entity.")
        except WacomServiceException as we:
            logging.error(we)
        # Shares the join key with user 2 and user 2 joins
        self.group_management.join_group(self.cache.token_2, self.cache.group_id, self.cache.join_key)
        groups: list[Group] = self.group_management.listing_groups(self.cache.token_2)
        self.assertEqual(len(groups), 1, "User 2 should only be in 1 group.")

    def test_5_add_user(self):
        """ Add user to group."""
        external_id_3 = str(uuid.uuid4())
        info, token, _, _ = self.user_management.create_user(self.tenant_api_key, external_id=external_id_3,
                                                             meta_data={'account-type': 'qa-test'},
                                                             roles=[UserRole.USER])
        self.group_management.add_user_to_group(self.cache.token, self.cache.group_id, info.id)

    def test_6_add_entity_to_group(self):
        """ Add entity to group."""
        # Adding entity to group
        groups: list[Group] = self.group_management.listing_groups(self.cache.token_2)
        self.group_management.add_entity_to_group(self.cache.token, groups[0].id, self.cache.thing_uri)
        entity: ThingObject = self.knowledge_client.entity(self.cache.token, self.cache.thing_uri)
        self.assertEqual(groups[0].id, entity.group_ids[0])
        self.knowledge_client.entity(self.cache.token_2, self.cache.thing_uri)
        self.group_management.remove_user_from_group(self.cache.token, self.cache.group_id, self.cache.internal_id_2,
                                                     force=True)
        try:
            self.knowledge_client.entity(self.cache.token_2, self.cache.thing_uri)
            self.fail("User 2 should not have access to the entity.")
        except WacomServiceException as we:
            pass
        groups: list[Group] = self.group_management.listing_groups(self.cache.token_2)
        self.assertEqual(len(groups), 0)
        self.group_management.join_group(self.cache.token_2, self.cache.group_id, self.cache.join_key)
        groups: list[Group] = self.group_management.listing_groups(self.cache.token_2)
        self.assertEqual(groups[0].id, entity.group_ids[0])
        self.knowledge_client.entity(self.cache.token_2, self.cache.thing_uri)

    def test_7_public_entity(self):
        """ Public entity."""
        full_entity: ThingObject = self.knowledge_client.entity(self.cache.token, self.cache.thing_uri)
        self.assertIsNotNone(full_entity)
        # Entity must not be empty
        full_entity.tenant_access_right.read = True
        self.knowledge_client.update_entity(self.cache.token, full_entity)
        pull_entity: ThingObject = self.knowledge_client.entity(self.cache.token_2, self.cache.thing_uri)
        self.assertIsNotNone(pull_entity)
        # This must fail
        try:
            self.knowledge_client.update_entity(self.cache.token_2, pull_entity)
            self.fail("User 2 should not have access to the entity.")
        except WacomServiceException as we:
            pass
        full_entity.tenant_access_right.write = True
        self.knowledge_client.update_entity(self.cache.token, full_entity)
        # Now we should have access
        pull_entity: ThingObject = self.knowledge_client.entity(self.cache.token_2, self.cache.thing_uri)
        self.assertIsNotNone(pull_entity)
        pull_entity.add_alias("Alias", LanguageCode('en_US'))
        self.knowledge_client.update_entity(self.cache.token_2, pull_entity)

    def test_8_delete_entity(self):
        """ Delete entity."""
        self.knowledge_client.delete_entity(self.cache.token, self.cache.thing_uri, force=True)

    def teardown_class(self):
        """ Clean up."""
        list_user_all: list[User] = self.user_management.listing_users(self.tenant_api_key, limit=GroupFlow.LIMIT)
        for u_i in list_user_all:
            if 'account-type' in u_i.meta_data and u_i.meta_data.get('account-type') == 'qa-test':
                logging.info(f'Clean user {u_i.external_user_id}')
                self.user_management.delete_user(self.tenant_api_key,
                                                 external_id=u_i.external_user_id, internal_id=u_i.id, force=True)
