# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
import urllib.parse
from typing import List, Any, Optional, Dict

import orjson

from knowledge.base.access import GroupAccessRight
from knowledge.base.ontology import NAME_TAG
from knowledge.services import (
    GROUP_USER_RIGHTS_TAG,
    JOIN_KEY_PARAM,
    USER_TO_ADD_PARAM,
    USER_TO_REMOVE_PARAM,
    FORCE_PARAM,
    DEFAULT_TIMEOUT,
)
from knowledge.services.asyncio.base import AsyncServiceAPIClient, handle_error
from knowledge.services.group import Group, GroupManagementService, GroupInfo

# -------------------------------------- Constant flags ----------------------------------------------------------------
from knowledge.services.users import FORCE_TAG, LIMIT_TAG, OFFSET_TAG


class AsyncGroupManagementService(AsyncServiceAPIClient):
    """
    Group Management Service API
    -----------------------------
    The service is managing groups.

    Functionality:
        - List all groups
        - Create group
        - Assign users to group
        - Share entities with group

    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    GROUP_ENDPOINT: str = "group"
    """"Endpoint for all group related functionality."""

    def __init__(
        self,
        application_name: str,
        service_url: str = AsyncServiceAPIClient.SERVICE_URL,
        service_endpoint: str = "graph/v1",
    ):
        super().__init__(application_name=application_name, service_url=service_url, service_endpoint=service_endpoint)

    # ------------------------------------------ Groups handling ------------------------------------------------------

    async def create_group(
        self,
        name: str,
        rights: GroupAccessRight = GroupAccessRight(read=True),
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Group:
        """
        Creates a group.

        Parameters
        ----------
        auth_key: str
            User key.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.

        Returns
        -------
        group: Group
            Instance of the group.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}"
        payload: Dict[str, str] = {NAME_TAG: name, GROUP_USER_RIGHTS_TAG: rights.to_list()}
        async_session = await self.asyncio_session()
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        response = await async_session.post(
            url,
            json=payload,
            timeout=timeout,
            verify_ssl=self.verify_calls,
            headers=headers,
        )
        if not response.ok:
            raise await handle_error("Creation of group failed.", response, payload=payload)
        group: Dict[str, Any] = await response.json(loads=orjson.loads)
        return Group.parse(group)

    async def update_group(
        self,
        group_id: str,
        name: str,
        rights: GroupAccessRight = GroupAccessRight,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Updates a group.

        Parameters
        ----------
        auth_key: str
            User key.
        group_id: str
            ID of the group.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}"
        payload: Dict[str, str] = {NAME_TAG: name, GROUP_USER_RIGHTS_TAG: rights.to_list()}
        async_session = await self.asyncio_session()
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        response = await async_session.patch(
            url,
            json=payload,
            timeout=timeout,
            verify_ssl=self.verify_calls,
            headers=headers,
        )
        if not response.ok:
            raise await handle_error("Update of group failed.", response, payload=payload)

    async def delete_group(
        self, group_id: str, force: bool = False, auth_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT
    ):
        """
         Delete a group.

         Parameters
         ----------
         group_id: str
             ID of the group.
         force: bool (Default = False)
            If True, the group will be deleted even if it is not empty.
         auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
         timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}"
        params: Dict[str, str] = {FORCE_TAG: str(force).lower()}
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        async_session = await self.asyncio_session()
        response = await async_session.delete(
            url,
            params=params,
            timeout=timeout,
            verify_ssl=self.verify_calls,
            headers=headers,
        )
        if not response.ok:
            raise await handle_error("Deletion of group failed.", response)

    async def listing_groups(
        self,
        admin: bool = False,
        limit: int = 20,
        offset: int = 0,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[Group]:
        """
        Listing all groups configured for this instance.

        Parameters
        ----------
        admin: bool (default:= False)
            Uses admin privilege to show all groups of the tenant.
            Requires user to have the role: TenantAdmin
        limit: int (default:= 20)
            Maximum number of groups to return.
        offset: int (default:= 0)
            Offset of the first group to return.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.

        Returns
        -------
        user:  List[Groups]
            List of groups.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}"
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        params: Dict[str, str] = {LIMIT_TAG: str(limit), OFFSET_TAG: str(offset)}
        if admin:
            url += "/admin"
        async_session = await self.asyncio_session()
        response = await async_session.get(
            url,
            params=params,
            timeout=timeout,
            verify_ssl=self.verify_calls,
            headers=headers,
        )
        if response.ok:
            groups: List[Dict[str, Any]] = await response.json(loads=orjson.loads)
        else:
            raise await handle_error("Listing of group failed.", response)
        return [Group.parse(g) for g in groups]

    async def group(self, group_id: str, auth_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT) -> GroupInfo:
        """Get a group.

        Parameters
        ----------
        group_id: str
            Group ID
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.

        Returns
        -------
        group: GroupInfo
            Instance of the group information.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}"
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        async_session = await self.asyncio_session()
        response = await async_session.get(
            url,
            timeout=timeout,
            verify_ssl=self.verify_calls,
            headers=headers,
        )
        if response.ok:
            group: Dict[str, Any] = await response.json(loads=orjson.loads)
        else:
            raise await handle_error("Getting of group information failed.", response)
        return GroupInfo.parse(group)

    async def join_group(
        self, group_id: str, join_key: str, auth_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT
    ):
        """User joining a group with his auth token.

        Parameters
        ----------
        group_id: str
            Group ID
        join_key: str
            Key which is used to join the group.
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/join"
        params: Dict[str, str] = {
            JOIN_KEY_PARAM: join_key,
        }
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        async_session = await self.asyncio_session()
        response = await async_session.post(
            url,
            params=params,
            timeout=timeout,
            verify_ssl=self.verify_calls,
            headers=headers,
        )
        if not response.ok:
            raise await handle_error("Joining of group failed.", response, parameters=params)

    async def leave_group(self, group_id: str, auth_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """User leaving a group with his auth token.

        Parameters
        ----------
        group_id: str
            Group ID
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/leave"
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        async_session = await self.asyncio_session()
        response = await async_session.post(url, headers=headers, timeout=timeout, verify_ssl=self.verify_calls)
        if not response.ok:
            raise await handle_error("Leaving of group failed.", response, headers=headers)

    async def add_user_to_group(
        self, group_id: str, user_id: str, auth_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT
    ):
        """Adding a user to group.

        Parameters
        ----------
        group_id: str
            Group ID
        user_id: str
            User who is added to the group
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/user/add"
        params: Dict[str, str] = {
            USER_TO_ADD_PARAM: user_id,
        }
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        async_session = await self.asyncio_session()
        response = await async_session.post(
            url, headers=headers, params=params, timeout=timeout, verify_ssl=self.verify_calls
        )
        if not response.ok:
            raise await handle_error("Adding of user to group failed.", response, headers=headers, parameters=params)

    async def remove_user_from_group(
        self,
        group_id: str,
        user_id: str,
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Remove a user from a group.

        Parameters
        ----------
        group_id: str
            Group ID
        user_id: str
            User who is remove from the group
        force: bool
            If true remove user and entities owned by the user if any
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/user/remove"
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        params: Dict[str, str] = {USER_TO_REMOVE_PARAM: user_id, FORCE_PARAM: str(force)}
        async_session = await self.asyncio_session()
        response = await async_session.post(
            url, headers=headers, params=params, timeout=timeout, verify_ssl=self.verify_calls
        )
        if not response.ok:
            raise await handle_error(
                "Removing of user from group failed.", response, headers=headers, parameters=params
            )

    async def add_entity_to_group(
        self,
        group_id: str,
        entity_uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Adding an entity to group.

        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            Entities URI
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (in seconds). Default: 60 seconds.
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        uri: str = urllib.parse.quote(entity_uri)
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/entity/{uri}/add"
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        async_session = await self.asyncio_session()
        response = await async_session.post(url, headers=headers, verify_ssl=self.verify_calls, timeout=timeout)
        if not response.ok:
            raise await handle_error("Adding of entity to group failed.", response, headers=headers)

    async def remove_entity_to_group(
        self,
        group_id: str,
        entity_uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Remove an entity from group.

        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            URI of entity
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (in seconds). Default: 60 seconds.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        uri: str = urllib.parse.quote(entity_uri)
        url: str = f"{self.service_base_url}{GroupManagementService.GROUP_ENDPOINT}/{group_id}/entity/{uri}/remove"
        headers: Dict[str, str] = await self._prepare_headers(overwrite_auth_token=auth_key)
        async_session = await self.asyncio_session()
        response = await async_session.post(url, headers=headers, verify_ssl=self.verify_calls, timeout=timeout)
        if not response.ok:
            raise await handle_error("Removing of entity from group failed.", response, headers=headers)
