# -*- coding: utf-8 -*-
# Copyright © 2023-24 Wacom. All rights reserved.
import logging
import os
import uuid
from typing import List, Optional
from unittest import TestCase

import pytest

from knowledge.services.users import UserManagementServiceAPI, User, UserRole


@pytest.fixture(scope="class")
def cache_class(request):
    """
    Fixture to store data for the test cases.
    """
    class ClassDB:
        """
        Class to store data for the test cases.
        """
        def __init__(self):
            self.__external_id: Optional[str] = None
            self.__token: Optional[str] = None

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
class UserFlow(TestCase):
    """
    Testing the user flow
    ---------------------
    - Create user
    - Check user
    - Delete user
    """
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=os.environ.get('INSTANCE'))
    '''User management service.'''
    tenant_api_key: str = os.environ.get('TENANT_API_KEY')
    LIMIT: int = 10000

    def test_1_create_user(self):
        """ Create user."""
        list_user_before: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=UserFlow.LIMIT)
        # Create an external user id
        self.cache.external_id = str(uuid.uuid4())
        # Create user
        user, token, _, _ = self.user_management.create_user(self.tenant_api_key,
                                                             external_id=self.cache.external_id,
                                                             meta_data={'account-type': 'qa-test'},
                                                             roles=[UserRole.USER])
        if user:
            self.user_token = token
            self.user_instance = user

        list_user_after: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=UserFlow.LIMIT)
        user_in_list: bool = False
        for u_i in list_user_after:
            if u_i.external_user_id == self.cache.external_id:
                user_in_list = True
                break
        # Check if user is created
        self.assertTrue(user_in_list, 'User is not created')
        # Ensure that more users are in the list than before
        self.assertGreater(len(list_user_after), len(list_user_before), 'There should be more users than before.')

    def test_2_check_user(self):
        """ Check user."""
        internal_id: str = self.user_management.user_internal_id(self.tenant_api_key, self.cache.external_id)
        self.assertIsNotNone(internal_id)

    def test_3_delete_user(self):
        """ Delete user."""
        list_user_before: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=UserFlow.LIMIT)
        user_in_list: bool = False
        for u_i in list_user_before:
            if u_i.external_user_id == self.cache.external_id:
                user_in_list = True
                break
        self.assertTrue(user_in_list, 'User is not available')

    def teardown_class(cls):
        """ Clean up the user."""
        list_user_all: List[User] = cls.user_management.listing_users(cls.tenant_api_key, limit=UserFlow.LIMIT)
        for u_i in list_user_all:
            if 'account-type' in u_i.meta_data and u_i.meta_data.get('account-type') == 'qa-test':
                logging.info(f'Clean user {u_i.external_user_id}')
                cls.user_management.delete_user(cls.tenant_api_key,
                                                external_id=u_i.external_user_id, internal_id=u_i.id, force=True)
