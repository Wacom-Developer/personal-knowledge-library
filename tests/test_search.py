# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import logging
import os
import uuid
from typing import List, Optional
from unittest import TestCase

import pytest
from ontospy import Ontospy

from knowledge.base.entity import LanguageCode
from knowledge.base.ontology import ThingObject, OntologyClassReference, OntologyPropertyReference, \
    SYSTEM_SOURCE_REFERENCE_ID
from knowledge.services.graph import WacomKnowledgeService, SearchPattern
from knowledge.services.group import GroupManagementServiceAPI
from knowledge.services.ontology import OntologyService
from knowledge.services.users import UserManagementServiceAPI, User, UserRole

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')
LEONARDO_DA_VINCI: str = 'Leonardo da Vinci'
MONA_LISA: str = 'Mona Lisa'
FIRST_NAME: str = 'Leonardo'
LAST_NAME: str = 'da Vinci'
HAS_ART_STYLE: OntologyPropertyReference = OntologyPropertyReference.parse('wacom:creative#hasArtstyle')


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
class SearchFlow(TestCase):
    """
    Testing the search flow
    ------------------------
    - Create a user
    - Create a join group with artist data

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

    def test_1_create_user(self):
        """ Create a user and join a group. """
        # Create an external user id
        self.cache.external_id = str(uuid.uuid4())
        # Create user
        _, token, refresh, expire = self.user_management.create_user(self.tenant_api_key,
                                                                     external_id=self.cache.external_id,
                                                                     meta_data={'account-type': 'qa-test'},
                                                                     roles=[UserRole.USER])
        self.cache.token = token

    def test_2_search_labels(self):
        res_entities, next_search_page = self.knowledge_client.search_labels(auth_key=self.cache.token,
                                                                             search_term=LEONARDO_DA_VINCI,
                                                                             language_code=LanguageCode('en_US'),
                                                                             limit=1000)

        self.assertGreaterEqual(len(res_entities), 1)

    def test_3_search_description(self):
        res_entities, next_search_page = self.knowledge_client.search_description(self.cache.token,
                                                                                  'Michelangelo\'s Sistine Chapel',
                                                                                  LanguageCode('en_US'), limit=1000)

        self.assertGreaterEqual(len(res_entities), 1)

    def test_4_search_relations(self):
        art_style: Optional[ThingObject] = None
        results, _ = self.knowledge_client.search_labels(self.cache.token, "portrait", LanguageCode('en_US'),
                                                         limit=1)
        for entity in results:
            art_style = entity
        res_entities, next_search_page = self.knowledge_client.search_relation(auth_key=self.cache.token,
                                                                               subject_uri=None,
                                                                               relation=HAS_ART_STYLE,
                                                                               object_uri=art_style.uri,
                                                                               language_code=LanguageCode('en_US'))

        self.assertGreaterEqual(len(res_entities), 1)

    def test_5_search_literals(self):
        res_entities, next_search_page = self.knowledge_client.search_literal(auth_key=self.cache.token,
                                                                              search_term="Q762",
                                                                              pattern=SearchPattern.REGEX,
                                                                              literal=SYSTEM_SOURCE_REFERENCE_ID,
                                                                              language_code=LanguageCode('en_US'))

        self.assertGreaterEqual(len(res_entities), 1)

    def teardown_class(self):
        list_user_all: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=SearchFlow.LIMIT)
        for u_i in list_user_all:
            if 'account-type' in u_i.meta_data and u_i.meta_data.get('account-type') == 'qa-test':
                logging.info(f'Clean user {u_i.external_user_id}')
                self.user_management.delete_user(self.tenant_api_key,
                                                 external_id=u_i.external_user_id, internal_id=u_i.id, force=True)
