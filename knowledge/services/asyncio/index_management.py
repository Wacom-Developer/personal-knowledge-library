# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
import json
from typing import Dict, Optional, AsyncIterator, Any, List

from knowledge.base.index import IndexMode, IndexDocument, HealthResponse
from knowledge.base.language import LocaleCode
from knowledge.services import (
    DEFAULT_TIMEOUT,
)
from knowledge.services.asyncio.base import (
    AsyncSession,
    ResponseData,
)
from knowledge.services.asyncio.search import AsyncSemanticSearchClient
from knowledge.services.base import WacomServiceException

__all__ = ["AsyncIndexManagementClient"]


class AsyncIndexManagementClient(AsyncSemanticSearchClient):
    """
    Async Index Management Client
    =============================
    Async client managing the index of the vector database.

    Parameters
    ----------
    service_url: str
        Service URL for the client.
    application_name: str (Default:= 'Async Semantic Search ')
        Name of the application.
    service_endpoint: str (Default:= 'vector/v1')
        Service endpoint for the client.
    verify_calls: bool (Default:= True)
        Whether to verify the calls to the service. If False, the client will not
        raise exceptions for non-2xx responses and will return the raw response data
        instead. This can be useful for debugging or when you want to handle errors
        manually.
    timeout: int (Default:= 60)
        Timeout for the request in seconds.
    """

    def __init__(
        self,
        service_url: str,
        application_name: str = "Async Index Management Client",
        base_auth_url: Optional[str] = None,
        service_endpoint: str = "vector/api/v1",
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

    async def index_health(
        self, index_mode: IndexMode, locale: LocaleCode, auth_key: Optional[str] = None
    ) -> HealthResponse:
        """
        Checks the health status of an index by sending an asynchronous POST request
        to the `/management/index/health/` endpoint of the service.

        Parameters
        ----------
        index_mode : IndexMode
            Mode identifier of the index to be checked ('document' or 'word').
        locale : LocaleCode
            Locale code that determines language or regional settings for the query.
        auth_key : Optional[str], optional
            Authentication token used to override the default session token.  If not
            supplied, the session's default token is used.

        Returns
        -------
        HealthResponse
            Response object containing the health status of the index.

        Raises
        ------
        WacomServiceException
            If the health check request fails.
        """
        url: str = f"{self.service_base_url}management/index/health/"
        session: AsyncSession = await self.asyncio_session()
        params: Dict[str, str] = {"index": index_mode, "locale": locale}
        response: ResponseData = await session.post(url, json=params, overwrite_auth_token=auth_key)

        if not response.ok:
            raise WacomServiceException(
                "Failed to check the index health.",
                url=url,
                method="POST",
                params=params,
                status_code=response.status,
                service_response=str(response.content) if response.content else None,
            )

        # ResponseData.content is already parsed as Dict when response is JSON
        if isinstance(response.content, dict):
            return HealthResponse.from_dict(response.content)
        raise WacomServiceException(
            "Unexpected response format from health check endpoint.",
            url=url,
            method="POST",
            params=params,
            status_code=response.status,
        )

    async def refresh_index(self, index_mode: IndexMode, locale: LocaleCode, auth_key: Optional[str] = None) -> None:
        """
        Refresh the index to make recent changes searchable.

        Parameters
        ----------
        index_mode : IndexMode
            Mode identifier of the index ('document' or 'word').
        locale : LocaleCode
            Locale code that determines language or regional settings.
        auth_key : Optional[str], optional
            Authentication token used to override the default session token.

        Raises
        ------
        WacomServiceException
            If the refresh request fails.
        """
        url: str = f"{self.service_base_url}management/index/refresh/"
        session: AsyncSession = await self.asyncio_session()
        params: Dict[str, str] = {"index": index_mode, "locale": locale}
        response: ResponseData = await session.post(url, json=params, overwrite_auth_token=auth_key)

        if not response.ok:
            raise WacomServiceException(
                "Failed to refresh the index.",
                url=url,
                method="POST",
                params=params,
                status_code=response.status,
                service_response=str(response.content) if response.content else None,
            )

    async def force_merge_index(
        self, index_mode: IndexMode, locale: LocaleCode, auth_key: Optional[str] = None
    ) -> None:
        """
        Force merge the index to optimize storage and performance.

        Parameters
        ----------
        index_mode : IndexMode
            Mode identifier of the index ('document' or 'word').
        locale : LocaleCode
            Locale code that determines language or regional settings.
        auth_key : Optional[str], optional
            Authentication token used to override the default session token.

        Raises
        ------
        WacomServiceException
            If the force merge request fails.
        """
        url: str = f"{self.service_base_url}management/index/optimize/"
        session: AsyncSession = await self.asyncio_session()
        params: Dict[str, str] = {"index": index_mode, "locale": locale}
        response: ResponseData = await session.post(url, json=params, overwrite_auth_token=auth_key)

        if not response.ok:
            raise WacomServiceException(
                "Failed to force merge the index.",
                url=url,
                method="POST",
                params=params,
                status_code=response.status,
                service_response=str(response.content) if response.content else None,
            )

    async def iterate_documents(
        self,
        index_mode: IndexMode,
        locale: LocaleCode,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> AsyncIterator[IndexDocument]:
        """
        Stream documents from the index as NDJSON (async version).

        This method asynchronously streams documents from the document store, allowing
        processing of large datasets without loading everything into memory. Documents
        are returned as they are read from the index.

        Parameters
        ----------
        index_mode : IndexMode
            Mode identifier of the index ('document' or 'word').
        locale : LocaleCode
            Locale code that determines language or regional settings.
        auth_key : Optional[str], optional
            Authentication token used to override the default session token.
        timeout : int, optional
            Request timeout in seconds (default: 60).

        Yields
        ------
        IndexDocument
            Each document as an IndexDocument instance containing:
            - id: Document identifier
            - content: Document content
            - content_uri: URI of the content
            - meta: Metadata (StreamedDocumentMeta) with creation time, locale, etc.

        Raises
        ------
        WacomServiceException
            If the streaming request fails or if NDJSON parsing fails.

        Examples
        -------
         Examples
        --------
        >>> from knowledge.services.asyncio.index_management import AsyncIndexManagementClient
        >>> from knowledge.base.language import EN_US
        >>>
        >>> async def main():
        >>>     client = AsyncIndexManagementClient(service_url="https://...")
        >>>     await client.login(tenant_api_key="<key>", external_user_id="<user>")
        >>>
        >>>     # Stream all documents from the index
        >>>     async for doc in client.iterate_documents("document", EN_US):
        ...         print(f"Document ID: {doc.id}")
        ...         print(f"Content: {doc.content[:100]}...")
        ...         print(f"Created: {doc.meta.creation}")
        ...         print(f"Locale: {doc.meta.locale}")
        """
        url: str = f"{self.service_base_url}management/index/stream/"
        params: Dict[str, str] = {"index": index_mode, "locale": locale}

        # Get the session and prepare headers
        session: AsyncSession = await self.asyncio_session()
        headers = await session._prepare_headers(overwrite_auth_token=auth_key)

        # Get the underlying aiohttp session
        aiohttp_session = await session._create_session()

        try:
            async with aiohttp_session.post(
                url,
                json=params,
                headers=headers,
                timeout=timeout,
            ) as response:
                if response.ok:
                    # Process NDJSON streamline by line
                    async for line in response.content:
                        if line:
                            try:
                                # Decode bytes to string and parse JSON
                                doc_dict: Dict[str, Any] = json.loads(line.decode("utf-8"))

                                # Check if this is an error message from the server
                                if "error" in doc_dict:
                                    raise WacomServiceException(
                                        f"Server error during streaming: {doc_dict.get('detail', 'Unknown error')}",
                                        url=url,
                                        method="POST",
                                        params=params,
                                        status_code=response.status,
                                    )

                                # Parse into IndexDocument
                                yield IndexDocument.from_dict(doc_dict)
                            except json.JSONDecodeError as e:
                                # Handle malformed JSON lines
                                raise WacomServiceException(
                                    f"Failed to parse NDJSON line: {e}",
                                    url=url,
                                    method="POST",
                                    params=params,
                                    status_code=response.status,
                                ) from e
                else:
                    error_text = await response.text()
                    raise WacomServiceException(
                        f"Failed to stream documents for index_mode={index_mode}, locale={locale}",
                        url=url,
                        method="POST",
                        params=params,
                        status_code=response.status,
                        service_response=error_text,
                    )
        except Exception as e:
            raise WacomServiceException(
                f"Error during document streaming: {str(e)}",
                url=url,
                method="POST",
                params=params,
            ) from e

    async def delete_document_by_id(
        self,
        index_mode: IndexMode,
        locale: LocaleCode,
        document_ids: List[str],
        auth_key: Optional[str] = None,
    ):
        """
        Deletes documents from the index.

        Parameters
        ----------
        index_mode : IndexMode
            Mode of indexing for the operation.
        locale : LocaleCode
            Locale code to specify the language or region context.
        document_ids : List[str]
            List of unique document identifiers to be removed from the index.
        auth_key : Optional[str], optional
            Authentication key for the request. If not provided, the default token is used.

        Raises
        ------
        WacomServiceException
            If the deletion request fails.
        """
        url: str = f"{self.service_base_url}management/index/entries/"
        params: Dict[str, Any] = {"index": index_mode, "locale": locale, "ids": document_ids}
        session: AsyncSession = await self.asyncio_session()
        response: ResponseData = await session.delete(url, json=params, overwrite_auth_token=auth_key)
        if not response.ok:
            raise WacomServiceException(
                "Failed to delete documents from the index.",
                url=url,
                method="DELETE",
                params=params,
                status_code=response.status,
                service_response=str(response.content) if response.content else None,
            )
