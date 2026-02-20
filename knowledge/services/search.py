# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
from typing import Dict, Any, Optional, List, Literal

from requests import Response

from knowledge.base.language import LocaleCode
from knowledge.base.search import (
    DocumentSearchResponse,
    LabelMatchingResponse,
    VectorDBDocument,
)
from knowledge.services import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF_FACTOR,
)
from knowledge.services.base import WacomServiceAPIClient, handle_error

__all__ = ["SemanticSearchClient"]


class SemanticSearchClient(WacomServiceAPIClient):
    """
    Semantic Search Client
    ======================
    Client for searching semantically similar documents and labels.

    Parameters
    ----------
    service_url: str
        Service URL for the client.
    service_endpoint: str (Default:= 'vector/v1')
        Service endpoint for the client.

    Examples
    --------
    >>> from knowledge.services.search import SemanticSearchClient
    >>> from knowledge.base.language import EN_US
    >>>
    >>> # Initialize the client
    >>> client = SemanticSearchClient(
    ...     service_url="https://private-knowledge.wacom.com"
    ... )
    >>> client.login(tenant_api_key="<tenant_key>", external_user_id="<user_id>")
    >>>
    >>> # Search for similar documents
    >>> results = client.search_documents(
    ...     query="machine learning",
    ...     locale=EN_US,
    ...     max_results=10
    ... )
    >>>
    >>> # Search for labels
    >>> labels = client.labels_search(
    ...     query="Einstein",
    ...     locale=EN_US,
    ...     max_results=5
    ... )
    """

    def __init__(
        self,
        service_url: str,
        application_name: str = "Semantic Search Client",
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

    def retrieve_documents_chunks(
        self,
        locale: LocaleCode,
        uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[VectorDBDocument]:
        """
        Retrieve document chunks from the vector index. The service is automatically chunking the document into
        smaller parts. The chunks are returned as a list of dictionaries, with metadata and content.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        uri: str
            URI of the document
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.
        Returns
        -------
        document: List[VectorDBDocument]:
            List of document chunks with metadata and content related to the document.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}documents/"
        response = self.request_session.get(
            url,
            params={"locale": locale, "uri": uri},
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return [VectorDBDocument(elem) for elem in response.json()]
        raise handle_error(
            "Failed to retrieve the document.",
            response,
            parameters={"locale": locale, "uri": uri},
        )

    def retrieve_labels(
        self,
        locale: LocaleCode,
        uri: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[VectorDBDocument]:
        """
        Retrieve labels from the vector index.

        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.

        Returns
        -------
        document: List[VectorDBDocument]
            List of labels with metadata and content related to the entity with uri.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}labels/"
        response: Response = self.request_session.get(
            url,
            params={"uri": uri, "locale": locale},
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return [VectorDBDocument(elem) for elem in response.json()]
        raise handle_error(
            "Failed to retrieve the labels.",
            response,
            parameters={"locale": locale, "uri": uri},
        )

    def count_documents(
        self,
        locale: LocaleCode,
        concept_type: Optional[str] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> int:
        """
        Count all documents for a tenant.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.

        Returns
        -------
        number_of_docs: int
            Number of documents.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}documents/count/"
        params: Dict[str, Any] = {"locale": locale}
        if concept_type:
            params["concept_type"] = concept_type
        response = self.request_session.get(
            url,
            params=params,
            overwrite_auth_token=auth_key,
            timeout=timeout,
        )
        if response.ok:
            return int(response.json().get("count", 0))
        raise handle_error("Counting documents failed.", response, parameters={"locale": locale})

    def count_documents_filter(
        self,
        locale: LocaleCode,
        filters: Dict[str, Any],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> int:
        """
        Count all documents for a tenant with filters.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.

        Returns
        -------
        number_of_docs: int
            Number of documents.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}documents/count/filter/"
        response: Response = self.request_session.post(
            url,
            json={"locale": locale, "filter": filters},
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return int(response.json().get("count", 0))
        raise handle_error(
            "Counting documents failed.",
            response,
            parameters={"locale": locale, "filter": filters},
        )

    def count_labels(
        self,
        locale: LocaleCode,
        concept_type: Optional[str] = None,
        auth_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> int:
        """
        Count all labels entries for a tenant.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        concept_type: Optional[str] (Default:= None)
            Concept type.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.
        auth_key: Optional[str] (Default:= None)
            If an auth key is provided, it will be used for the request.
        Returns
        -------
        count: int
            Number of words.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}labels/count/"
        params: Dict[str, Any] = {"locale": locale}
        if concept_type:
            params["concept_type"] = concept_type
        response = self.request_session.get(
            url,
            params=params,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return int(response.json().get("count", 0))
        raise handle_error("Counting labels failed.", response, parameters={"locale": locale})

    def count_labels_filter(
        self,
        locale: LocaleCode,
        filters: Dict[str, Any],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> int:
        """
        Count all labels for a tenant with filters.

        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.
        Returns
        -------
        number_of_docs: int
            Number of labels.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}labels/count/filter/"
        response: Response = self.request_session.post(
            url,
            json={"locale": locale, "filter": filters},
            overwrite_auth_token=auth_key,
            timeout=timeout,
        )
        if response.ok:
            return int(response.json().get("count", 0))
        raise handle_error(
            "Counting labels failed.",
            response,
            parameters={"locale": locale, "filter": filters},
        )

    def document_search(
        self,
        query: str,
        locale: LocaleCode,
        filters: Optional[Dict[str, Any]] = None,
        max_results: int = 10,
        filter_mode: Optional[Literal["AND", "OR"]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> DocumentSearchResponse:
        """
        Async Semantic search.

        Parameters
        ----------
        query: str
            Query text for the search
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Optional[Dict[str, Any]] = None
            Filters for the search
        max_results: int
            Maximum number of results
        filter_mode: Optional[Literal["AND", "OR"]] = None
            Filter mode for the search. If None is provided, the default is "AND".
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.
        Returns
        -------
        search_results: DocumentSearchResponse
            Search results response.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}documents/search/"
        params: Dict[str, Any] = {
            "query": query,
            "metadata": filters if filters else {},
            "locale": locale,
            "max_results": max_results,
        }
        if filter_mode:
            params["filter_mode"] = filter_mode
        response: Response = self.request_session.post(
            url,
            json=params,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            response_dict: Dict[str, Any] = response.json()
            return DocumentSearchResponse.from_dict(response_dict)
        raise handle_error("Semantic Search failed.", response, parameters=params)

    def labels_search(
        self,
        query: str,
        locale: LocaleCode,
        filters: Optional[Dict[str, Any]] = None,
        filter_mode: Optional[Literal["AND", "OR"]] = None,
        max_results: int = 10,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> LabelMatchingResponse:
        """
        Async search for semantically similar labels.

        Parameters
        ----------
        query: str
            Query text for the search
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Optional[Dict[str, Any]] = None
            Filters for the search
        max_results: int
            Maximum number of results
        filter_mode: Optional[Literal["AND", "OR"]] = None
            Filter mode for the search. If None is provided, the default is "AND".
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.

        Returns
        -------
        list_entities: Dict[str, Any]
            Search results response.
        """
        url: str = f"{self.service_base_url}labels/match/"
        params: Dict[str, Any] = {
            "query": query,
            "metadata": filters if filters else {},
            "locale": locale,
            "max_results": max_results,
        }
        if filter_mode:
            params["filter_mode"] = filter_mode
        response = self.request_session.post(
            url,
            json=params,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            response_dict: Dict[str, Any] = response.json()
            return LabelMatchingResponse.from_dict(response_dict)
        raise handle_error("Label fuzzy matching failed.", response, parameters=params)
