# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
import asyncio
from typing import Dict, Any, Optional, List, Literal

import orjson

from knowledge.base.language import LocaleCode
from knowledge.base.queue import QueueNames, QueueCount, QueueMonitor
from knowledge.base.search import DocumentSearchResponse, LabelMatchingResponse, VectorDBDocument
from knowledge.services import (
    DEFAULT_TIMEOUT,
    AUTHORIZATION_HEADER_FLAG,
    APPLICATION_JSON_HEADER,
    CONTENT_TYPE_HEADER_FLAG,
    USER_AGENT_HEADER_FLAG,
)
from knowledge.services.asyncio.base import AsyncServiceAPIClient, handle_error


class AsyncSemanticSearchClient(AsyncServiceAPIClient):
    """
    Semantic Search Client
    ======================
    Client for searching semantically similar documents and labels.

    Parameters
    ----------
    service_url: str
        Service URL for the client.
    application_name: str (Default:= 'Async Semantic Search ')
        Name of the application.
    service_endpoint: str (Default:= 'vector/v1')
        Service endpoint for the client.
    """

    def __init__(self, service_url: str, application_name: str = "Async Semantic Search ",
                 service_endpoint: str = "vector/api/v1"):
        super().__init__(application_name, service_url, service_endpoint)

    async def retrieve_document_chunks(
        self, locale: LocaleCode, uri: str, auth_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT
    ) -> List[VectorDBDocument]:
        """
        Retrieve document chunks from vector database. The service is automatically chunking the document into
        smaller parts. The chunks are returned as a list of dictionaries, with metadata and content.

        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (default: 60 seconds)

        Returns
        -------
        document: Dict[str, Any]
            List of document chunks with metadata and content related to the document.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}documents/"

        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        async with self.__async_session__() as session:
            async with session.get(
                url, params={"locale": locale, "uri": uri}, headers=headers, timeout=timeout
            ) as response:
                if response.ok:
                    docs: List[VectorDBDocument] = [
                        VectorDBDocument(vec_doc) for vec_doc in await response.json(loads=orjson.loads)
                    ]
                else:
                    raise await handle_error(
                        "Failed to retrieve the document.",
                        response,
                        headers=headers,
                        parameters={"locale": locale, "uri": uri},
                    )
        await asyncio.sleep(0.25 if self.use_graceful_shutdown else 0.0)
        return docs

    async def retrieve_labels(
        self, locale: LocaleCode, uri: str, auth_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT
    ) -> List[VectorDBDocument]:
        """
        Retrieve labels from a vector database.

        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (default: 60 seconds)

        Returns
        -------
        document: List[VectorDBDocument]
            List of labels with metadata and content related to the entity with uri.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}labels/"

        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        async with self.__async_session__() as session:
            async with session.get(
                url, params={"locale": locale, "uri": uri}, headers=headers, timeout=timeout
            ) as response:
                if response.ok:
                    docs: List[VectorDBDocument] = [
                        VectorDBDocument(vec_doc) for vec_doc in await response.json(loads=orjson.loads)
                    ]
                else:
                    raise await handle_error(
                        "Failed to retrieve the document.",
                        response,
                        headers=headers,
                        parameters={"locale": locale, "uri": uri},
                    )
        await asyncio.sleep(0.25 if self.use_graceful_shutdown else 0.0)
        return docs

    async def count_documents(
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
        locale: str
            Locale
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (default: 60 seconds)

        Returns
        -------
        number_of_docs: int
            Number of documents.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}documents/count/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {"locale": locale}
        if concept_type:
            params["concept_type"] = concept_type
        async with self.__async_session__() as session:
            async with session.get(url, params=params, headers=headers, timeout=timeout) as response:
                if response.ok:
                    count: int = (await response.json(loads=orjson.loads)).get("count", 0)
                else:
                    raise await handle_error(
                        "Counting documents failed.", response, headers=headers, parameters={"locale": locale}
                    )
        await asyncio.sleep(0.25 if self.use_graceful_shutdown else 0.0)
        return count

    async def count_documents_filter(
        self,
        locale: LocaleCode,
        filters: Dict[str, Any],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> int:
        """
        Count all documents for a tenant using a filter.

        Parameters
        ----------
        locale: str
            Locale
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (default: 60 seconds).

        Returns
        -------
        number_of_docs: int
            Number of documents.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}documents/count/filter/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        async with self.__async_session__() as session:
            async with session.post(
                url, json={"locale": locale, "filter": filters}, timeout=timeout, headers=headers
            ) as response:
                if response.ok:
                    count: int = (await response.json(loads=orjson.loads)).get("count", 0)
                else:
                    raise await handle_error(
                        "Counting documents failed.",
                        response,
                        headers=headers,
                        parameters={"locale": locale, "filter": filters},
                    )
        await asyncio.sleep(0.25 if self.use_graceful_shutdown else 0.0)
        return count

    async def count_labels(
        self,
        locale: str,
        concept_type: Optional[str] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> int:
        """
        Count all labels entries for a tenant.

        Parameters
        ----------
        locale: str
            Locale
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If auth key is provided, it will be used for the request.
        timeout: int
            Default timeout for the request (default: 60 seconds)

        Returns
        -------
        count: int
            Number of words.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}labels/count/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {"locale": locale}
        if concept_type:
            params["concept_type"] = concept_type
        async with self.__async_session__() as session:
            async with session.get(url, params=params, headers=headers, timeout=timeout) as response:
                if response.ok:
                    count: int = (await response.json(loads=orjson.loads)).get("count", 0)
                else:
                    raise await handle_error(
                        "Counting labels failed.", response, headers=headers, parameters={"locale": locale}
                    )
        await asyncio.sleep(0.25 if self.use_graceful_shutdown else 0.0)
        return count

    async def count_labels_filter(
        self,
        locale: LocaleCode,
        filters: Dict[str, Any],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> int:
        """
        Count all labels for a tenant using a filter.

        Parameters
        ----------
        locale: str
            Locale
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (default: 60 seconds).

        Returns
        -------
        number_of_docs: int
            Number of documents.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}labels/count/filter/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        async with self.__async_session__() as session:
            async with session.post(
                url, json={"locale": locale, "filter": filters}, timeout=timeout, headers=headers
            ) as response:
                if response.ok:
                    count: int = (await response.json(loads=orjson.loads)).get("count", 0)
                else:
                    raise await handle_error(
                        "Counting documents failed.",
                        response,
                        headers=headers,
                        parameters={"locale": locale, "filter": filters},
                    )
        await asyncio.sleep(0.25 if self.use_graceful_shutdown else 0.0)
        return count

    async def document_search(
        self,
        query: str,
        locale: str,
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
        locale: str
            Locale of the text
        filters: Optional[Dict[str, Any]] = None
            Filters for the search
        max_results: int
            Maximum number of results
        filter_mode: Optional[Literal["AND", "OR"]] = None
            Filter mode for the search. If None is provided, the default is "AND".
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (default: 60 seconds)
        Returns
        -------
        response: DocumentSearchResponse
            Search results response.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}documents/search/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {
            "query": query,
            "metadata": filters if filters else {},
            "locale": locale,
            "max_results": max_results,
        }
        if filter_mode:
            params["filter_mode"] = filter_mode
        session = await self.session()
        async with session.post(url, headers=headers, json=params, timeout=timeout) as response:
            if response.ok:
                response_dict: Dict[str, Any] = await response.json(loads=orjson.loads)
            else:
                raise await handle_error("Semantic Search failed.", response, headers=headers, parameters=params)
        return DocumentSearchResponse.from_dict(response_dict)

    async def labels_search(
        self,
        query: str,
        locale: str,
        filters: Optional[Dict[str, Any]] = None,
        max_results: int = 10,
        filter_mode: Optional[Literal["AND", "OR"]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> LabelMatchingResponse:
        """
        Async search for semantically similar labels.

        Parameters
        ----------
        query: str
            Query text for the search
        locale: str
            Locale of the text
        filters: Optional[Dict[str, Any]] = None
            Filters for the search
        max_results: int
            Maximum number of results
        filter_mode: Optional[Literal["AND", "OR"]] = None
            Filter mode for the search. If None is provided, the default is "AND".
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (default: 60 seconds).
        Returns
        -------
        response: LabelMatchingResponse
            Search results response.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}labels/match/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, Any] = {
            "query": query,
            "metadata": filters if filters else {},
            "locale": locale,
            "max_results": max_results,
        }
        if filter_mode:
            params["filter_mode"] = filter_mode
        session = await self.session()
        async with session.post(url, headers=headers, json=params, timeout=timeout) as response:
            if response.ok:
                response_dict: Dict[str, Any] = await response.json(loads=orjson.loads)
            else:
                raise await handle_error(
                    "Label fuzzy matching failed.", response, headers=headers, parameters=params
                )
        return LabelMatchingResponse.from_dict(response_dict)

    async def list_queues(self, auth_key: Optional[str] = None) -> QueueNames:
        """
        List all available queues in the semantic search service.

        Parameters
        ----------
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.

        Returns
        -------
        queues: QueueNames
            List of queue names.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}queues/names/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        session = await self.session()
        async with session.get(url, headers=headers) as response:
            if response.ok:
                queues: Dict[str, List[str]] = await response.json(loads=orjson.loads)
                return QueueNames.parse_json(queues)
            else:
                raise await handle_error("Failed to list queues.", response, headers=headers)

    async def queue_is_empty(self, queue_name: str, auth_key: Optional[str] = None) -> bool:
        """
        Checks if a given queue is empty.

        This asynchronous method checks whether the specified queue exists and if it is
        empty by interacting with a remote service. It uses an authorization key for
        authentication, and if not provided, retrieves it using a helper method.

        Parameters
        ----------
        queue_name : str
            The name of the queue to check.
        auth_key : Optional[str], optional
            Authorization key used for authenticating with the service. Defaults
            to None, in which case the method will fetch an appropriate token.

        Returns
        -------
        bool
            True if the specified queue is empty, False otherwise.
        """
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}queues/empty/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, str] = {
            "queue_name": queue_name
        }
        session = await self.session()
        async with session.get(url, headers=headers, params=params) as response:
            if response.ok:
                is_empty: bool = await response.json(loads=orjson.loads)
                return is_empty
            else:
                raise await handle_error("Failed to check if the queue is empty.", response, headers=headers)

    async def queue_size(self, queue_name: str, auth_key: Optional[str] = None) -> QueueCount:
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}queues/count/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, str] = {
            "queue_name": queue_name
        }
        session = await self.session()
        async with session.get(url, headers=headers, params=params) as response:
            if response.ok:
                response_structure: Dict[str, Any] =  await response.json(loads=orjson.loads)
                return QueueCount.parse_json(response_structure)
            else:
                raise await handle_error("Failed to get the queue size.", response, headers=headers)

    async def queue_monitor_information(self, queue_name: str, auth_key: Optional[str] = None) -> QueueMonitor:
        if auth_key is None:
            auth_key, _ = await self.handle_token()
        url: str = f"{self.service_base_url}queues/"
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER,
            AUTHORIZATION_HEADER_FLAG: f"Bearer {auth_key}",
        }
        params: Dict[str, str] = {
            "queue_name": queue_name
        }
        session = await self.session()
        async with session.get(url, headers=headers, params=params) as response:
            if response.ok:
                response_structure: Dict[str, Any] =  await response.json(loads=orjson.loads)
                return QueueMonitor.parse_json(response_structure)
            else:
                raise await handle_error("Failed to get the queue monitor information.", response,
                                         headers=headers)

