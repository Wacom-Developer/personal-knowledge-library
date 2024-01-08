# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom. All rights reserved.
from datetime import datetime
from typing import Any, Union, Dict, List, Tuple

import orjson
import requests
from dateutil.parser import parse, ParserError
from requests import Response

from knowledge.services.asyncio.base import AsyncServiceAPIClient
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException
from knowledge.services.users import UserRole, USER_AGENT_TAG, TENANT_API_KEY_FLAG, OFFSET_TAG, LIMIT_TAG, User, \
    USER_ID_TAG, EXTERNAL_USER_ID_TAG, FORCE_TAG, ROLES_TAG, META_DATA_TAG, CONTENT_TYPE_FLAG, DEFAULT_TIMEOUT, \
    INTERNAL_USER_ID_TAG


class AsyncUserManagementService(AsyncServiceAPIClient):
    """
    User-Management Service API
    -----------------------------

    Functionality:
        - List all users
        - Create / update / delete users

    Parameters
    ----------
    application_name: str
        Name of the application
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    USER_DETAILS_ENDPOINT: str = f'{WacomServiceAPIClient.USER_ENDPOINT}/internal-id'

    def __init__(self, application_name: str, service_url: str = WacomServiceAPIClient.SERVICE_URL,
                 service_endpoint: str = 'graph/v1'):
        super().__init__(application_name=application_name, service_url=service_url, service_endpoint=service_endpoint)

    # ------------------------------------------ Users handling --------------------------------------------------------

    async def create_user(self, tenant_key: str, external_id: str, meta_data: Dict[str, str] = None,
                          roles: List[UserRole] = None) -> Tuple[User, str, str, datetime]:
        """
        Creates user for a tenant.

        Parameters
        ----------
        tenant_key: str -
            API key for tenant
        external_id: str -
            External id of user identification service.
        meta_data: Dict[str, str]
            Meta-data dictionary.
        roles: List[UserRole]
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
        url: str = f'{self.service_base_url}{AsyncUserManagementService.USER_ENDPOINT}'
        headers: dict = {
            USER_AGENT_TAG: self.user_agent,
            TENANT_API_KEY_FLAG: tenant_key,
            CONTENT_TYPE_FLAG: 'application/json'
        }
        payload: dict = {
            EXTERNAL_USER_ID_TAG: external_id,
            META_DATA_TAG: meta_data if meta_data is not None else {},
            ROLES_TAG: [r.value for r in roles] if roles is not None else [UserRole.USER.value]
        }
        async with self.__async_session__() as session:
            async with session.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT,
                                    verify_ssl=self.verify_calls) as response:
                if response.ok:
                    results: Dict[str, Union[str, Dict[str, str], List[str]]] = await response.json(loads=orjson.loads)

                    try:
                        date_object: datetime = parse(results['token']['expirationDate'])
                    except (ParserError, OverflowError) as _:
                        date_object: datetime = datetime.now()
                    return User.parse(results['user']), results['token']['accessToken'], \
                        results['token']['refreshToken'], date_object

            raise WacomServiceException(f'Response code:={response.status}, exception:= {response.text}')

    async def update_user(self, tenant_key: str, internal_id: str, external_id: str, meta_data: Dict[str, str] = None,
                          roles: List[UserRole] = None):
        """Updates user for a tenant.

        Parameters
        ----------
        tenant_key: str
            API key for tenant
        internal_id: str
            Internal id of semantic service.
        external_id: str
            External id of user identification service.
        meta_data: Dict[str, str]
            Meta-data dictionary.
        roles: List[UserRole]
            List of roles.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{AsyncUserManagementService.USER_ENDPOINT}'
        headers: Dict[str, str] = {
            USER_AGENT_TAG: self.user_agent,
            TENANT_API_KEY_FLAG: tenant_key,
            CONTENT_TYPE_FLAG: 'application/json'
        }
        payload: Dict[str, str] = {
            META_DATA_TAG: meta_data if meta_data is not None else {},
            ROLES_TAG: [r.value for r in roles] if roles is not None else [UserRole.USER.value]
        }
        params: Dict[str, str] = {
            USER_ID_TAG: internal_id,
            EXTERNAL_USER_ID_TAG: external_id
        }
        response: Response = requests.patch(url, headers=headers, json=payload, params=params, timeout=DEFAULT_TIMEOUT,
                                            verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Updating user failed. '
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    async def delete_user(self, tenant_key: str, external_id: str, internal_id: str, force: bool = False):
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
        url: str = f'{self.service_base_url}{AsyncUserManagementService.USER_ENDPOINT}'
        headers: Dict[str, str] = {
            USER_AGENT_TAG: self.user_agent,
            TENANT_API_KEY_FLAG: tenant_key
        }
        params: Dict[str, str] = {
            USER_ID_TAG: internal_id,
            EXTERNAL_USER_ID_TAG: external_id,
            FORCE_TAG: force
        }
        response: Response = requests.delete(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT,
                                             verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    async def user_internal_id(self, tenant_key: str, external_id: str) -> str:
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
        url: str = f'{self.service_base_url}{AsyncUserManagementService.USER_DETAILS_ENDPOINT}'
        headers: dict = {
            USER_AGENT_TAG: self.user_agent,
            TENANT_API_KEY_FLAG: tenant_key
        }
        parameters: Dict[str, str] = {
            EXTERNAL_USER_ID_TAG:  external_id
        }
        response: Response = requests.get(url, headers=headers, params=parameters, timeout=DEFAULT_TIMEOUT,
                                          verify=self.verify_calls)
        if response.ok:
            response_dict: Dict[str, Any] = response.json()
            return response_dict[INTERNAL_USER_ID_TAG]
        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    async def listing_users(self, tenant_key: str, offset: int = 0, limit: int = 20) -> List[User]:
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
        user: List[User]
            List of users.
        """
        url: str = f'{self.service_base_url}{AsyncUserManagementService.USER_ENDPOINT}'
        headers: Dict[str, str] = {
            USER_AGENT_TAG: self.user_agent,
            TENANT_API_KEY_FLAG: tenant_key
        }
        params: Dict[str, str] = {
            OFFSET_TAG: offset,
            LIMIT_TAG: limit
        }
        response: Response = requests.get(url, headers=headers, params=params,  timeout=DEFAULT_TIMEOUT,
                                          verify=self.verify_calls)
        if response.ok:
            users: List[Dict[str, Any]] = response.json()
            results: List[User] = []
            for u in users:
                results.append(User.parse(u))
            return results
        raise WacomServiceException(f'Listing of users failed.'
                                    f'Response code:={response.status_code}, exception:= {response.text}')
