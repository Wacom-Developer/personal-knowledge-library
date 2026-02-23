# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
import json
from typing import Dict, Optional, Iterator, Any, List

from requests import Response

from knowledge.base.index import (
    HealthResponse,
    IndexMode,
    IndexDocument,
)
from knowledge.base.language import LocaleCode
from knowledge.services import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_TIMEOUT,
)
from knowledge.services.base import handle_error, WacomServiceException
from knowledge.services.search import SemanticSearchClient


class IndexManagementClient(SemanticSearchClient):
    """
    Index Management Client
    ========================
    Client for searching managing the index.

    Parameters
    ----------
    service_url: str
        Service URL for the client.
    service_endpoint: str (Default:= 'vector/v1')
        Service endpoint for the client.
    """

    def __init__(
        self,
        service_url: str,
        application_name: str = "Index Management Client",
        base_auth_url: Optional[str] = None,
        service_endpoint: str = "vector/api/v1",
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

    def iterate_documents(
        self,
        index_mode: IndexMode,
        locale: LocaleCode,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Iterator[IndexDocument]:
        """
        Stream documents from the index as NDJSON.

        This method streams documents from the document store, allowing processing
        of large datasets without loading everything into memory. Documents are
        returned as they are read from the index.

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
        --------
        >>> from knowledge.services.index_management import IndexManagementClient
        >>> from knowledge.base.language import EN_US
        >>>
        >>> client = IndexManagementClient(service_url="https://...")
        >>> client.login(tenant_api_key="<key>", external_user_id="<user>")
        >>>
        >>> # Stream all documents from the index
        >>> for doc in client.iterate_documents("document", EN_US):
        ...     print(f"Document ID: {doc.id}")
        ...     print(f"Content: {doc.content[:100]}...")
        ...     print(f"Created: {doc.meta.creation}")
        ...     print(f"Locale: {doc.meta.locale}")

        """
        url: str = f"{self.service_base_url}management/index/stream/"
        params: Dict[str, str] = {"index": index_mode, "locale": locale}

        response: Response = self.request_session.post(
            url,
            json=params,
            timeout=timeout,
            overwrite_auth_token=auth_key,
            stream=True,
        )

        if response.ok:
            # Process NDJSON-stream line by line
            for line in response.iter_lines():
                if line:
                    try:
                        # Decode bytes to string and parse JSON
                        doc_dict: Dict[str, Any] = json.loads(line.decode("utf-8"))

                        # Check if this is an error message from the server
                        if "error" in doc_dict:
                            raise handle_error(
                                f"Server error during streaming: {doc_dict.get('detail', 'Unknown error')}",
                                response,
                                parameters=params,
                            )

                        # Parse into IndexDocument
                        yield IndexDocument.from_dict(doc_dict)
                    except json.JSONDecodeError as e:
                        # Handle malformed JSON lines
                        raise handle_error(
                            f"Failed to parse NDJSON line: {e}",
                            response,
                            parameters=params,
                        ) from e
        else:
            raise handle_error(
                f"Failed to stream documents for index_mode={index_mode}, locale={locale}",
                response,
                parameters=params,
            )

    def index_health(self, index_mode: IndexMode, locale: LocaleCode, auth_key: Optional[str] = None) -> HealthResponse:
        """
        Checks the health status of an index by sending an asynchronous GET request
        to the `/index/health` endpoint of the service.  The response content is
        printed directly to standard output.

        Parameters
        ----------
        index_mode : str
            Mode identifier of the index to be checked.
        locale : LocaleCode
            Locale code that determines language or regional settings for the query.
        auth_key : Optional[str], optional
            Authentication token used to override the default session token.  If not
            supplied, the session’s default token is used.

        Returns
        -------
        HealthResponse
            Response object containing the health status of the index.

        """
        url: str = f"{self.service_base_url}management/index/health/"
        params: Dict[str, str] = {"index": index_mode, "locale": locale}
        response: Response = self.request_session.post(url, json=params, overwrite_auth_token=auth_key)

        if not response.ok:
            raise handle_error("Failed to check the index health.", response)
        data = response.json()
        return HealthResponse.from_dict(data)

    def refresh_index(self, index_mode: IndexMode, locale: LocaleCode, auth_key: Optional[str] = None) -> None:
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
        params: Dict[str, str] = {"index": index_mode, "locale": locale}
        response: Response = self.request_session.post(url, json=params, overwrite_auth_token=auth_key)
        if not response.ok:
            raise handle_error("Failed to refresh the index.", response)

    def force_merge_index(self, index_mode: IndexMode, locale: LocaleCode, auth_key: Optional[str] = None) -> None:
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
        params: Dict[str, str] = {"index": index_mode, "locale": locale}
        response: Response = self.request_session.post(url, json=params, overwrite_auth_token=auth_key)
        if not response.ok:
            raise handle_error("Failed to force merge the index.", response)

    def delete_document_by_id(
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
        response: Response = self.request_session.delete(url, json=params, overwrite_auth_token=auth_key)
        if not response.ok:
            raise WacomServiceException(
                "Failed to delete documents from the index.",
                url=url,
                method="DELETE",
                params=params,
                status_code=response.status_code,
                service_response=str(response.content) if response.content else None,
            )


__all__ = ["IndexManagementClient"]
