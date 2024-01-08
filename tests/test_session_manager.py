# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom. All rights reserved.
import logging
import os
import uuid
from typing import List, Optional
from unittest import TestCase

import pytest

from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.session import TokenManager, Session, PermanentSession, TimedSession
from knowledge.services.users import UserManagementServiceAPI, User, UserRole


@pytest.fixture(scope="class")
def cache_class(request):
    class ClassDB:
        """
        Class to store data for the test cases.
        """

        def __init__(self):
            self.__external_id_1: Optional[str] = None
            self.__external_id_2: Optional[str] = None

        @property
        def external_id_1(self) -> Optional[str]:
            return self.__external_id_1

        @external_id_1.setter
        def external_id_1(self, external_id: Optional[str]):
            self.__external_id_1 = external_id

        @property
        def external_id_2(self) -> Optional[str]:
            return self.__external_id_2

        @external_id_2.setter
        def external_id_2(self, external_id: Optional[str]):
            self.__external_id_2 = external_id

    # set a class attribute on the invoking test context
    request.cls.cache = ClassDB()


@pytest.mark.usefixtures("cache_class")
class SessionManagerTest(TestCase):
    """
    Test cases for the session manager.
    ----------------------------------
    The session manager is responsible for the creation of the user and the session token.
    """
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=os.environ.get('INSTANCE'))
    '''User management service.'''
    tenant_api_key: str = os.environ.get('TENANT_API_KEY')
    LIMIT: int = 10000

    def test_1_create_user(self):
        """ Create user."""
        # Create an external user id
        self.cache.external_id_1 = str(uuid.uuid4())
        self.cache.external_id_2 = str(uuid.uuid4())
        # Create user
        self.user_management.create_user(self.tenant_api_key,
                                         external_id=self.cache.external_id_1,
                                         meta_data={'account-type': 'qa-test'},
                                         roles=[UserRole.USER])
        # Create user
        self.user_management.create_user(self.tenant_api_key,
                                         external_id=self.cache.external_id_2,
                                         meta_data={'account-type': 'qa-test'},
                                         roles=[UserRole.USER])

    def test_2_session_manager(self):
        """ Check session manager."""
        knowledge_service: WacomKnowledgeService = WacomKnowledgeService(application_name="Session manager 1",
                                                                         service_url=os.environ.get('INSTANCE'))
        # Token manager
        token_manager_1: TokenManager = TokenManager()
        token_manager_2: TokenManager = TokenManager()
        # Ensure that the token manager is a singleton
        self.assertEqual(id(token_manager_1), id(token_manager_2), "The token manager is not a singleton.")
        user_token, refresh_token, _ = knowledge_service.request_user_token(self.tenant_api_key,
                                                                            self.cache.external_id_1)
        # Add user session
        session: PermanentSession = token_manager_1.add_session(user_token, refresh_token,
                                                                self.tenant_api_key, self.cache.external_id_1)
        self.assertIsInstance(session, PermanentSession, "The session is not a permanent session.")
        self.assertEqual(session.external_user_id, self.cache.external_id_1)
        self.assertEqual(session.tenant_api_key, self.tenant_api_key)
        self.assertLessEqual(session.expires_in, 3600.)
        # The token is valid for 1 hour (3600 seconds)
        self.assertGreaterEqual(session.service_url, os.environ.get('INSTANCE', "")
                                .replace('https://', '').replace('http://', ''))


    def test_3_login(self):
        knowledge_service_1: WacomKnowledgeService = WacomKnowledgeService(application_name="Session manager 1",
                                                                           service_url=os.environ.get('INSTANCE'))
        knowledge_service_2: WacomKnowledgeService = WacomKnowledgeService(application_name="Session manager 1",
                                                                           service_url=os.environ.get('INSTANCE'))
        # Check if user is created
        knowledge_service_1.login(self.tenant_api_key, self.cache.external_id_1)
        knowledge_service_2.login(self.tenant_api_key, self.cache.external_id_2)

    def test_4_duplicate(self):
        knowledge_service_1: WacomKnowledgeService = WacomKnowledgeService(application_name="Session manager 1",
                                                                           service_url=os.environ.get('INSTANCE'))
        knowledge_service_2: WacomKnowledgeService = WacomKnowledgeService(application_name="Session manager 1",
                                                                           service_url=os.environ.get('INSTANCE'))
        self.assertNotEqual(self.cache.external_id_1, self.cache.external_id_2,
                            "The external ids are equal, but they should not be.")
        # Check if user is created
        session_id_1 = knowledge_service_1.login(self.tenant_api_key, self.cache.external_id_1)
        session_id_2 = knowledge_service_2.login(self.tenant_api_key, self.cache.external_id_1)
        session_id_3 = knowledge_service_1.login(self.tenant_api_key, self.cache.external_id_2)
        self.assertEqual(session_id_1.id, session_id_2.id, "The session ids are not equal, but they should be")
        self.assertNotEqual(session_id_1.id, session_id_3.id, "The session ids are equal, but they should not")
        self.assertNotEqual(session_id_2.id, session_id_3.id, "The session ids are equal, but they should not.")

    def test_5_refresh(self):
        """Test the refresh of the token."""
        knowledge_service_1: WacomKnowledgeService = WacomKnowledgeService(application_name="Session manager 1",
                                                                           service_url=os.environ.get('INSTANCE'))
        # Check if user is created
        session: Session = knowledge_service_1.login(self.tenant_api_key, self.cache.external_id_1)
        knowledge_service_1.handle_token(force_refresh=True)
        # Now, we overwrite the token with a TimedSession
        timed_session: Session = knowledge_service_1.register_token(session.auth_token)
        self.assertIsInstance(timed_session, TimedSession, "The session is not a session.")
        try:
            knowledge_service_1.handle_token(force_refresh=True)
            self.fail("The token is not refreshable, but the handle token method did not raise an exception.")
        except Exception as e:
            self.assertIsInstance(e, WacomServiceException, "The exception is not a WacomServiceException.")

    def teardown_class(cls):
        """ Clean up the user."""
        list_user_all: List[User] = cls.user_management.listing_users(cls.tenant_api_key,
                                                                      limit=SessionManagerTest.LIMIT)
        for u_i in list_user_all:
            if 'account-type' in u_i.meta_data and u_i.meta_data.get('account-type') == 'qa-test':
                logging.info(f'Clean user {u_i.external_user_id}')
                cls.user_management.delete_user(cls.tenant_api_key,
                                                external_id=u_i.external_user_id, internal_id=u_i.id, force=True)
