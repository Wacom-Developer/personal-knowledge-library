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

from knowledge.base.language import JA_JP, EN_US, DE_DE
from knowledge.base.ontology import ThingObject, OntologyClassReference
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService, Visibility
from knowledge.services.group import GroupManagementService, Group
from knowledge.services.ontology import OntologyService
from knowledge.services.users import UserManagementServiceAPI, User, UserRole
from knowledge.utils.graph import count_things

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')


def create_thing() -> ThingObject:
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse('wacom:core#Person'))
    for lang_inst in [JA_JP, EN_US, DE_DE]:
        fake: Faker = Faker(lang_inst)
        name: str = fake.name()
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
    group_management: GroupManagementService = GroupManagementService(service_url=os.environ.get('INSTANCE'))

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
        before: int = count_things(self.knowledge_client, self.cache.token, THING_OBJECT, only_own=True)
        uri_thing: str = self.knowledge_client.create_entity(thing, auth_key=self.cache.token)
        after: int = count_things(self.knowledge_client, self.cache.token, THING_OBJECT, only_own=True)
        self.assertEqual(before + 1, after, "Entity was not created.")
        self.cache.thing_uri = uri_thing
        self.knowledge_client.set_entity_image_local(uri_thing,
                                                     Path(__file__).parent / '..' / 'assets' / 'dummy.png',
                                                     auth_key=self.cache.token)

    def test_3_create_group(self):
        """ Create group."""
        # Now, user 1 creates a group
        g: Group = self.group_management.create_group("qa-test-group", auth_key=self.cache.token)
        self.cache.group_id = g.id
        self.cache.join_key = g.join_key

    def test_4_join_group(self):
        """ Join group."""
        self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token)
        try:
            self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token_2)
            self.fail("User 2 should not have access to the entity.")
        except WacomServiceException as we:
            logging.error(we)
        # Shares the join key with user 2 and user 2 joins
        self.group_management.join_group(self.cache.group_id, self.cache.join_key, auth_key=self.cache.token_2)
        groups: List[Group] = self.group_management.listing_groups(auth_key=self.cache.token_2)
        self.assertEqual(len(groups), 1, "User 2 should only be in 1 group.")

    def test_5_add_user(self):
        """ Add user to group."""
        external_id_3 = str(uuid.uuid4())
        info, token, _, _ = self.user_management.create_user(self.tenant_api_key, external_id=external_id_3,
                                                             meta_data={'account-type': 'qa-test'},
                                                             roles=[UserRole.USER])
        self.group_management.add_user_to_group(self.cache.group_id, info.id, auth_key=self.cache.token)

    def test_6_add_entity_to_group(self):
        """ Add entity to group."""
        # Adding entity to group
        groups: List[Group] = self.group_management.listing_groups(auth_key=self.cache.token_2)
        before_shared_count: int = count_things(self.knowledge_client, self.cache.token, THING_OBJECT,
                                                visibility=Visibility.SHARED, only_own=True)
        self.assertEqual(before_shared_count, 0, "User 1 should not have access to the entity.")
        before_shared_count_u2: int = count_things(self.knowledge_client, self.cache.token_2, THING_OBJECT,
                                                   visibility=Visibility.SHARED, only_own=False)
        self.assertEqual(before_shared_count_u2, 0, "User 2 should not have access to the entity.")
        self.group_management.add_entity_to_group(groups[0].id, self.cache.thing_uri, auth_key=self.cache.token)
        after_shared_count: int = count_things(self.knowledge_client, self.cache.token, THING_OBJECT,
                                               visibility=Visibility.SHARED, only_own=True)
        after_shared_count_u2: int = count_things(self.knowledge_client, self.cache.token_2, THING_OBJECT,
                                                  visibility=Visibility.SHARED, only_own=False)
        self.assertEqual(after_shared_count, 1, "User 1 should have one shared entity.")
        self.assertEqual(after_shared_count_u2, 1, "User 2 should have one shared entity.")

        entity: ThingObject = self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token)
        self.assertEqual(groups[0].id, entity.group_ids[0])
        self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token_2)
        self.group_management.remove_user_from_group(self.cache.group_id, self.cache.internal_id_2,
                                                     force=True, auth_key=self.cache.token)
        try:
            self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token_2)
            self.fail("User 2 should not have access to the entity.")
        except WacomServiceException as we:
            pass
        after_removal_shared_count_u2: int = count_things(self.knowledge_client, self.cache.token_2, THING_OBJECT,
                                                          visibility=Visibility.SHARED, only_own=False)
        self.assertEqual(after_removal_shared_count_u2, 0, "User 2 should not have access to the entity.")
        groups: List[Group] = self.group_management.listing_groups(auth_key=self.cache.token_2)
        self.assertEqual(len(groups), 0)
        self.group_management.join_group(self.cache.group_id, self.cache.join_key, auth_key=self.cache.token_2)
        groups: List[Group] = self.group_management.listing_groups(auth_key=self.cache.token_2)
        self.assertEqual(groups[0].id, entity.group_ids[0])
        self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token_2)

    def test_7_public_entity(self):
        """ Public entity."""
        full_entity: ThingObject = self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token)
        self.assertIsNotNone(full_entity)
        # Entity must not be empty
        full_entity.tenant_access_right.read = True
        self.knowledge_client.update_entity(full_entity, auth_key=self.cache.token)
        pull_entity: ThingObject = self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token_2)
        self.assertIsNotNone(pull_entity)
        # This must fail
        try:
            self.knowledge_client.update_entity(pull_entity, auth_key=self.cache.token_2)
            self.fail("User 2 should not have access to the entity.")
        except WacomServiceException as we:
            pass
        full_entity.tenant_access_right.write = True
        self.knowledge_client.update_entity(full_entity, auth_key=self.cache.token)
        # Now we should have access
        pull_entity: ThingObject = self.knowledge_client.entity(self.cache.thing_uri, auth_key=self.cache.token_2)
        self.assertIsNotNone(pull_entity)
        pull_entity.add_alias("Alias", EN_US)
        self.knowledge_client.update_entity(pull_entity, auth_key=self.cache.token_2)

    def test_8_delete_entity(self):
        """ Delete entity."""
        self.knowledge_client.delete_entity(self.cache.thing_uri, force=True, auth_key=self.cache.token)

    def teardown_class(self):
        """ Clean up."""
        list_user_all: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=GroupFlow.LIMIT)
        for u_i in list_user_all:
            if 'account-type' in u_i.meta_data and u_i.meta_data.get('account-type') == 'qa-test':
                logging.info(f'Clean user {u_i.external_user_id}')
                self.user_management.delete_user(self.tenant_api_key,
                                                 external_id=u_i.external_user_id, internal_id=u_i.id, force=True)
