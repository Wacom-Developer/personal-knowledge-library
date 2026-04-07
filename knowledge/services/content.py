# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""
Content Service Client
----------------------
Synchronous client for the Wacom Content API providing operations for:
- Uploading content files linked to entity URIs
- Retrieving content files and metadata
- Updating content files, metadata, and tags
- Deleting content items
"""
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from requests import Response

from knowledge.base.content import ContentObject
from knowledge.services import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF_FACTOR,
)
from knowledge.services.base import WacomServiceAPIClient, handle_error

__all__ = ["ContentClient"]


class ContentClient(WacomServiceAPIClient):
    """
    ContentClient
    -------------
    Synchronous client for the Wacom Content API.

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
    verify_calls: bool
        Flag if API calls should be verified (default: True)
    max_retries: int
        Maximum number of retries for failed requests
    backoff_factor: float
        Backoff factor for retries

    Examples
    --------
    >>> from knowledge.services.content import ContentClient
    >>>
    >>> client = ContentClient(service_url="https://private-knowledge.wacom.com")
    >>> client.login(tenant_api_key="<key>", external_user_id="<user_id>")
    >>>
    >>> with open("document.pdf", "rb") as f:
    ...     content_id = client.upload_content(
    ...         uri="wacom:entity:123", file_content=f.read(), filename="document.pdf"
    ...     )
    """

    CONTENT_ENDPOINT: str = "content"

    def __init__(
        self,
        service_url: str,
        application_name: str = "Content Client",
        base_auth_url: Optional[str] = None,
        service_endpoint: str = "graph/v1",
        verify_calls: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        super().__init__(
            service_url=service_url,
            application_name=application_name,
            base_auth_url=base_auth_url,
            service_endpoint=service_endpoint,
            verify_calls=verify_calls,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    def _content_url(self, path: str = "") -> str:
        """Build a content API URL for the given version and optional sub-path."""
        return f"{self.service_base_url}{self.CONTENT_ENDPOINT}/{path}"

    # ------------------------------------------ Upload ----------------------------------------------------------------

    def upload_content(
        self,
        uri: str,
        file_content: bytes,
        filename: str,
        mimetype: str,
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
        mimetype: str
            MIME type of the file (e.g., "application/pdf").
        auth_key: Optional[str] = (Default:= None)
            If set, uses this auth key instead of the logged-in user's token.
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
        response: Response = self.request_session.post(
            url,
            files={"file": (filename, file_content, mimetype)},
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
            ignore_content_type=True,
        )
        if response.status_code == HTTPStatus.OK:
            return response.text.strip('"')
        raise handle_error("Uploading content failed.", response)

    # ------------------------------------------ Retrieve --------------------------------------------------------------

    def list_content(
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
            If set, uses this auth key instead of the logged-in user's token.
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
        response: Response = self.request_session.get(
            url,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return [ContentObject.from_dict(item) for item in response.json()]
        raise handle_error("Retrieving content list failed.", response, parameters=params)

    def download_content(
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
            If set, uses this auth key instead of the logged-in user's token.
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
        response: Response = self.request_session.get(
            url,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return response.content
        raise handle_error("Downloading content failed.", response)

    def get_content_info(
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
            If set, uses this auth key instead of the logged-in user's token.
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
        response: Response = self.request_session.get(
            url,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return ContentObject.from_dict(response.json())
        raise handle_error("Retrieving content info failed.", response)

    # ------------------------------------------ Update ----------------------------------------------------------------

    def update_content(
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
        tags: Optional[List[str]] = (Default:= None)
            Updated tags. Pass an empty list to clear existing values.
        auth_key: Optional[str] = (Default:= None)
            If set, uses this auth key instead of the logged-in user's token.
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
        response: Response = self.request_session.patch(
            url,
            json=payload,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return ContentObject.from_dict(response.json())
        raise handle_error("Updating content failed.", response, payload=payload)

    def update_content_file(
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
            If set, uses this auth key instead of the logged-in user's token.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(f"{content_id}/file")
        response: Response = self.request_session.put(
            url,
            files={"file": (filename, file_content)},
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
            ignore_content_type=True,
        )
        if response.status_code == HTTPStatus.OK:
            return
        raise handle_error("Updating content file failed.", response)

    def update_content_metadata(
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
            If set, uses this auth key instead of the logged-in user's token.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(f"{content_id}/metadata")
        payload: Dict[str, Any] = {"metadata": metadata}
        response: Response = self.request_session.patch(
            url,
            json=payload,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return
        raise handle_error("Updating content metadata failed.", response, payload=payload)

    def update_content_tags(
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
            If set, uses this auth key instead of the logged-in user's token.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url(f"{content_id}/tags")
        payload: Dict[str, Any] = {"tags": tags}
        response: Response = self.request_session.patch(
            url,
            json=payload,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return
        raise handle_error("Updating content tags failed.", response, payload=payload)

    # ------------------------------------------ Delete ----------------------------------------------------------------

    def delete_all_content(
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
            If set, uses this auth key instead of the logged-in user's token.
        timeout: int
            Request timeout in seconds.

        Raises
        ------
        WacomServiceException
            If the service returns an error.
        """
        url: str = self._content_url()
        params: Dict[str, str] = {"uri": uri}
        response: Response = self.request_session.delete(
            url,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return
        raise handle_error("Deleting all content failed.", response, parameters=params)

    def delete_content(
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
        force: Optional[bool]
            If set, the content will be deleted regardless of additional validation rules.
        auth_key: Optional[str] = (Default:= None)
            If set, uses this auth key instead of the logged-in user's token.
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
        response: Response = self.request_session.delete(
            url,
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.status_code == HTTPStatus.OK:
            return
        raise handle_error("Deleting content failed.", response, parameters=params)
