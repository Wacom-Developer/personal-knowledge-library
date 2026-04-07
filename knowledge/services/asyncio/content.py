# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
from http import HTTPStatus
from typing import Dict, List, Optional, Any

import aiohttp

from knowledge.base.content import ContentObject
from knowledge.services import DEFAULT_TIMEOUT
from knowledge.services.asyncio.base import (
    AsyncServiceAPIClient,
    AsyncSession,
    handle_error,
    ResponseData,
)

__all__ = ["AsyncContentClient"]


class AsyncContentClient(AsyncServiceAPIClient):
    """
    AsyncContentClient
    ------------------
    Async client for the Content API.

    Provides operations for:
        - Uploading content files linked to entity URIs
        - Retrieving content files and metadata
        - Updating content files, metadata, and tags
        - Deleting content items

    Parameters
    ----------
    service_url: str
        URL of the service
    application_name: str
        Name of the application using the service
    base_auth_url: Optional[str] = (Default:= None)
        Base auth URL
    service_endpoint: str
        Service endpoint URL
    verify_calls: bool
        Flag if API calls should be verified (default: True)
    timeout: int
        Default timeout for requests in seconds

    Examples
    --------
    >>> import asyncio
    >>> from knowledge.services.asyncio.content import AsyncContentClient
    >>>
    >>> async def main():
    ...     client = AsyncContentClient(
    ...         service_url="https://private-knowledge.wacom.com",
    ...         application_name="My App"
    ...     )
    ...     await client.login(tenant_api_key="<key>", external_user_id="<user_id>")
    ...
    ...     with open("document.pdf", "rb") as f:
    ...         content_id = await client.upload_content(
    ...             uri="wacom:entity:123", file_content=f.read(), filename="document.pdf"
    ...         )
    >>>
    >>> asyncio.run(main())
    """

    CONTENT_ENDPOINT: str = "content"

    def __init__(
        self,
        service_url: str,
        application_name: str = "Async Content Client",
        base_auth_url: Optional[str] = None,
        service_endpoint: str = "graph/v1",
        verify_calls: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        super().__init__(
            service_url=service_url,
            application_name=application_name,
            base_auth_url=base_auth_url,
            service_endpoint=service_endpoint,
            verify_calls=verify_calls,
            timeout=timeout,
        )

    def _content_url(self, path: str = "") -> str:
        """Build a content API URL for the given version and optional sub-path."""
        return f"{self.service_base_url}{self.CONTENT_ENDPOINT}/{path}"

    # ------------------------------------------ Upload ----------------------------------------------------------------

    async def upload_content(
        self,
        uri: str,
        file_content: bytes,
        filename: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> str:
        """
        Upload a new content file associated with the specified entity URI.

        Parameters
        ----------
        uri: str
            URI of the entity this content belongs to.
        file_content: bytes
            Binary content of the file to upload.
        filename: str
            Name of the file (used as the filename in the multipart form).
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Returns
        -------
        content_id: str
            Unique identifier of the created content item.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(uri)
        form: aiohttp.FormData = aiohttp.FormData()
        form.add_field("file", file_content, filename=filename)
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.post(
            url,
            data=form,
            timeout=timeout,
            overwrite_auth_token=auth_key,
            ignore_content_type=True,
        )
        if response.status == HTTPStatus.OK:
            content = response.content
            return content.decode() if isinstance(content, bytes) else str(content)
        raise await handle_error("Uploading content failed.", response)

    # ------------------------------------------ Retrieve --------------------------------------------------------------

    async def list_content(
        self,
        uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[ContentObject]:
        """
        Retrieve information for all content associated with a specific entity.

        Parameters
        ----------
        uri: str
            URI of the entity whose content should be retrieved.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Returns
        -------
        content_items: List[ContentObject]
            List of content items linked to the entity.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url()
        params: Dict[str, str] = {"uri": uri}
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.get(
            url,
            params=params,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            items = response.content
            if isinstance(items, list):
                return [ContentObject.from_dict(item) for item in items]
            return []
        raise await handle_error("Retrieving content list failed.", response, parameters=params)

    async def download_content(
        self,
        content_id: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bytes:
        """
        Retrieve the file associated with the specified content identifier.

        Parameters
        ----------
        content_id: str
            Unique identifier of the content.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Returns
        -------
        file_content: bytes
            The stored file content.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(content_id)
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.get(
            url,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            content = response.content
            return content if isinstance(content, bytes) else str(content).encode()
        raise await handle_error("Downloading content failed.", response)

    async def get_content_info(
        self,
        content_id: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> ContentObject:
        """
        Retrieve the metadata associated with the specified content identifier.

        Parameters
        ----------
        content_id: str
            Unique identifier of the content.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Returns
        -------
        content_object: ContentObject
            Metadata of the content item.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(f"{content_id}/info")
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.get(
            url,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            return ContentObject.from_dict(response.content)  # type: ignore[arg-type]
        raise await handle_error("Retrieving content info failed.", response)

    # ------------------------------------------ Update ----------------------------------------------------------------

    async def update_content(
        self,
        content_id: str,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> ContentObject:
        """
        Update content metadata and tags (partial update).

        If a property is None it will not be modified. If metadata or tags are
        empty, the existing values will be removed.

        Parameters
        ----------
        content_id: str
            Unique identifier of the content.
        metadata: Optional[Dict[str, str]]
            Updated key-value metadata. Pass an empty dict to clear existing values.
        tags: Optional[List[str]]
            Updated tags. Pass an empty list to clear existing values.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Returns
        -------
        content_object: ContentObject
            Updated content item.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(content_id)
        payload: Dict[str, Any] = {}
        if metadata is not None:
            payload["metadata"] = metadata
        if tags is not None:
            payload["tags"] = tags
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.patch(
            url,
            json=payload,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            return ContentObject.from_dict(response.content)  # type: ignore[arg-type]
        raise await handle_error("Updating content failed.", response, payload=payload)

    async def update_content_file(
        self,
        content_id: str,
        file_content: bytes,
        filename: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Replace the stored file for an existing content item.

        Parameters
        ----------
        content_id: str
            Unique identifier of the content.
        file_content: bytes
            Binary content of the updated file.
        filename: str
            Name of the file.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(f"{content_id}/file")
        form: aiohttp.FormData = aiohttp.FormData()
        form.add_field("file", file_content, filename=filename)
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.put(
            url,
            data=form,
            timeout=timeout,
            overwrite_auth_token=auth_key,
            ignore_content_type=True,
        )
        if response.status == HTTPStatus.OK:
            return
        raise await handle_error("Updating content file failed.", response)

    async def update_content_metadata(
        self,
        content_id: str,
        metadata: Optional[Dict[str, str]],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Update the metadata of a content item.

        If metadata is None it will not be modified. If metadata is an empty dict,
        the existing values will be removed.

        Parameters
        ----------
        content_id: str
            Unique identifier of the content.
        metadata: Optional[Dict[str, str]]
            Updated key-value metadata.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(f"{content_id}/metadata")
        payload: Dict[str, Any] = {"metadata": metadata}
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.patch(
            url,
            json=payload,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            return
        raise await handle_error("Updating content metadata failed.", response, payload=payload)

    async def update_content_tags(
        self,
        content_id: str,
        tags: Optional[List[str]],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Update the tags of a content item.

        If tags is None it will not be modified. If tags is an empty list,
        the existing values will be removed.

        Parameters
        ----------
        content_id: str
            Unique identifier of the content.
        tags: Optional[List[str]]
            Updated tags.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(f"{content_id}/tags")
        payload: Dict[str, Any] = {"tags": tags}
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.patch(
            url,
            json=payload,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            return
        raise await handle_error("Updating content tags failed.", response, payload=payload)

    # ------------------------------------------ Delete ----------------------------------------------------------------

    async def delete_all_content(
        self,
        uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Delete all content associated with the specified entity URI.

        Parameters
        ----------
        uri: str
            URI of the entity whose content should be removed.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url()
        params: Dict[str, str] = {"uri": uri}
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.delete(
            url,
            params=params,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            return
        raise await handle_error("Deleting all content failed.", response, parameters=params)

    async def delete_content(
        self,
        content_id: str,
        force: Optional[bool] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Delete the specified content item.

        Parameters
        ----------
        content_id: str
            Unique identifier of the content.
        force: Optional[bool] = (Default:= None)
            If set, the content will be deleted regardless of additional validation rules.
        auth_key: Optional[str] = (Default:= None)
            Use a different auth key than the one from the client.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(content_id)
        params: Dict[str, Any] = {}
        if force is not None:
            params["force"] = str(force).lower()
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.delete(
            url,
            params=params,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.status == HTTPStatus.OK:
            return
        raise await handle_error("Deleting content failed.", response, parameters=params)
