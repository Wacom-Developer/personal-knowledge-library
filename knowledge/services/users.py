# -*- coding: utf-8 -*-
# Copyright © 2021-23 Wacom. All rights reserved.
import enum
from datetime import datetime
from typing import Any, Union

import requests
from dateutil.parser import parse, ParserError
from requests import Response

from knowledge.services import USER_AGENT_STR
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException

# -------------------------------------- Constant flags ----------------------------------------------------------------
TENANT_ID: str = 'tenantId'
USER_ID_TAG: str = 'userId'
LIMIT_TAG: str = 'limit'
OFFSET_TAG: str = 'offset'
ROLES_TAG: str = 'roles'
META_DATA_TAG: str = 'metadata'
INTERNAL_USER_ID_TAG: str = 'internalUserId'
EXTERNAL_USER_ID_TAG: str = 'externalUserId'
FORCE_TAG: str = 'force'
CONTENT_TYPE_FLAG: str = 'Content-Type'
TENANT_API_KEY_FLAG: str = 'x-tenant-api-key'
USER_AGENT_TAG: str = "User-Agent"


class UserRole(enum.Enum):
    """
    UserRole
    --------
    Roles of the users in
    """
    USER = 'User'
    """User only has control over his personal entities."""
    ADMIN = 'TenantAdmin'
    """TenantAdmin has access to all entities independent of the access rights."""


USER_ROLE_MAPPING: dict[str, UserRole] = dict([(str(r.value), r) for r in UserRole])


class User:
    """
    User
    -----
    In Personal Knowledge backend is linking a user to a shadow user which is used within the personal knowledge graph.

    Parameters
    ----------
    tenant_id: str
        Tenant id
    user_id: str
        User id
    external_user_id: str
        External user id, referencing the user to authentication system.
    meta_data: dict[str, Any]
        Metadata associated with user.
    user_roles: list[UserRole]
        List of user roles.
    """

    def __init__(self, tenant_id: str, user_id: str, external_user_id: str, meta_data: dict[str, Any],
                 user_roles: list[UserRole]):
        self.__tenant_id: str = tenant_id
        self.__user_id: str = user_id
        self.__external_user_id: str = external_user_id
        self.__meta_data: dict[str, Any] = meta_data
        self.__user_roles: list[UserRole] = user_roles

    @property
    def id(self) -> str:
        """User id."""
        return self.__user_id

    @property
    def tenant_id(self) -> str:
        """Tenant ID."""
        return self.__tenant_id

    @property
    def external_user_id(self) -> str:
        """External user id, referencing to external user authentication."""
        return self.__external_user_id

    @property
    def meta_data(self) -> dict[str, Any]:
        """Meta data for user."""
        return self.__meta_data

    @meta_data.setter
    def meta_data(self, value: dict[str, Any]):
        self.__meta_data = value

    @property
    def user_roles(self) -> list[UserRole]:
        """List of user roles"""
        return self.__user_roles

    @classmethod
    def parse(cls, param: dict[str, Any]) -> 'User':
        """
        Parse user from dictionary.
        Parameters
        ----------
        param: dict[str, Any]
            Dictionary containing user information.

        Returns
        -------
        user: User
            Instance of user.
        """
        user_id: str = param['id']
        tenant_id: str = param[TENANT_ID]
        external_user_id: str = param['externalUserId']
        meta_data: dict[str, Any] = {}
        if META_DATA_TAG in param and param[META_DATA_TAG] is not None:
            meta_data = param[META_DATA_TAG]
        # Support the old version of the user management service
        elif 'metaData' in param:
            meta_data = param['metaData']
        user_roles: list[UserRole] = [USER_ROLE_MAPPING[r] for r in param['roles']]
        return User(tenant_id=tenant_id, user_id=user_id, external_user_id=external_user_id, meta_data=meta_data,
                    user_roles=user_roles)

    def __repr__(self):
        return f'<User: id:={self.id}, external user id:={self.external_user_id}, user roles:= {self.user_roles}]>'


class UserManagementServiceAPI(WacomServiceAPIClient):
    """
    User-Management Service API
    -----------------------------

    Functionality:
        - List all users
        - Create / update / delete users

    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    USER_DETAILS_ENDPOINT: str = f'{WacomServiceAPIClient.USER_ENDPOINT}/internal-id'

    def __init__(self, service_url: str = WacomServiceAPIClient.SERVICE_URL, service_endpoint: str = 'graph/v1'):
        super().__init__("UserManagementServiceAPI", service_url=service_url, service_endpoint=service_endpoint)

    # ------------------------------------------ Users handling --------------------------------------------------------

    def create_user(self, tenant_key: str, external_id: str, meta_data: dict[str, str] = None,
                    roles: list[UserRole] = None) -> tuple[User, str, str, datetime]:
        """
        Creates user for a tenant.

        Parameters
        ----------
        tenant_key: str -
            API key for tenant
        external_id: str -
            External id of user identification service.
        meta_data: dict[str, str]
            Meta-data dictionary.
        roles: list[UserRole]
            List of roles.

        Returns
        -------
        user: User
            Instance of the user
        token: str
            Auth token for user
        refresh_key: str
            Refresh token
        expiration_time: datetime
            Expiration time
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{UserManagementServiceAPI.USER_ENDPOINT}'
        headers: dict = {
            USER_AGENT_TAG: USER_AGENT_STR,
            TENANT_API_KEY_FLAG: tenant_key,
            CONTENT_TYPE_FLAG: 'application/json'
        }
        payload: dict = {
            EXTERNAL_USER_ID_TAG: external_id,
            META_DATA_TAG: meta_data if meta_data is not None else {},
            ROLES_TAG: [r.value for r in roles] if roles is not None else [UserRole.USER.value]
        }
        response: Response = requests.post(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            results: dict[str, Union[str, dict[str, str], list[str]]] = response.json()

            try:
                date_object: datetime = parse(results['token']['expirationDate'])
            except (ParserError, OverflowError) as _:
                date_object: datetime = datetime.now()

            return User.parse(results['user']), results['token']['accessToken'], results['token']['refreshToken'], \
                date_object

        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    def update_user(self, tenant_key: str, internal_id: str, external_id: str, meta_data: dict[str, str] = None,
                    roles: list[UserRole] = None):
        """Updates user for a tenant.

        Parameters
        ----------
        tenant_key: str
            API key for tenant
        internal_id: str
            Internal id of semantic service.
        external_id: str
            External id of user identification service.
        meta_data: dict[str, str]
            Meta-data dictionary.
        roles: list[UserRole]
            List of roles.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{UserManagementServiceAPI.USER_ENDPOINT}'
        headers: dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            TENANT_API_KEY_FLAG: tenant_key,
            CONTENT_TYPE_FLAG: 'application/json'
        }
        payload: dict[str, str] = {
            META_DATA_TAG: meta_data if meta_data is not None else {},
            ROLES_TAG: [r.value for r in roles] if roles is not None else [UserRole.USER.value]
        }
        params: dict[str, str] = {
            USER_ID_TAG: internal_id,
            EXTERNAL_USER_ID_TAG: external_id
        }
        response: Response = requests.patch(url, headers=headers, json=payload, params=params, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Updating user failed. '
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def delete_user(self, tenant_key: str, external_id: str, internal_id: str, force: bool = False):
        """Deletes user from tenant.

        Parameters
        ----------
        tenant_key: str
            API key for tenant
        external_id: str
            External id of user identification service.
        internal_id: str
            Internal id of user.
        force: bool
            If set to true removes all user data including groups and entities.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{UserManagementServiceAPI.USER_ENDPOINT}'
        headers: dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            TENANT_API_KEY_FLAG: tenant_key
        }
        params: dict[str, str] = {
            USER_ID_TAG: internal_id,
            EXTERNAL_USER_ID_TAG: external_id,
            FORCE_TAG: force
        }
        response: Response = requests.delete(url, headers=headers, params=params, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    def user_internal_id(self, tenant_key: str, external_id: str) -> str:
        """User internal id.

        Parameters
        ----------
        tenant_key: str
            API key for tenant
        external_id: str
            External id of user

        Returns
        -------
        internal_user_id: str
            Internal id of users

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{UserManagementServiceAPI.USER_DETAILS_ENDPOINT}'
        headers: dict = {
            USER_AGENT_TAG: USER_AGENT_STR,
            TENANT_API_KEY_FLAG: tenant_key
        }
        parameters: dict[str, str] = {
            EXTERNAL_USER_ID_TAG:  external_id
        }
        response: Response = requests.get(url, headers=headers, params=parameters, verify=self.verify_calls)
        if response.ok:
            response_dict: dict[str, Any] = response.json()
            return response_dict[INTERNAL_USER_ID_TAG]
        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    def listing_users(self, tenant_key: str, offset: int = 0, limit: int = 20) -> list[User]:
        """
        Listing all users configured for this instance.

        Parameters
        ----------
        tenant_key: str
            API key for tenant
        offset: int - [optional]
            Offset value to define starting position in list. [DEFAULT:= 0]
        limit: int - [optional]
            Define the limit of the list size. [DEFAULT:= 20]

        Returns
        -------
        user: list[User]
            List of users.
        """
        url: str = f'{self.service_base_url}{UserManagementServiceAPI.USER_ENDPOINT}'
        headers: dict[str, str] = {
            USER_AGENT_TAG: USER_AGENT_STR,
            TENANT_API_KEY_FLAG: tenant_key
        }
        params: dict[str, str] = {
            OFFSET_TAG: offset,
            LIMIT_TAG: limit
        }
        response: Response = requests.get(url, headers=headers, params=params, verify=self.verify_calls)
        if response.ok:
            users: list[dict[str, Any]] = response.json()
            results: list[User] = []
            for u in users:
                results.append(User.parse(u))
            return results
        raise WacomServiceException(f'Listing of users failed.'
                                    f'Response code:={response.status_code}, exception:= {response.text}')
