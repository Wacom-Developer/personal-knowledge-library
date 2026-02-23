Module knowledge.services.asyncio.index_management
==================================================

Classes
-------

`AsyncIndexManagementClient(service_url: str, application_name: str = 'Async Index Management Client', base_auth_url: str | None = None, service_endpoint: str = 'vector/api/v1', verify_calls: bool = True, timeout: int = 60)`
:   Async Index Management Client
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

    ### Ancestors (in MRO)

    * knowledge.services.asyncio.search.AsyncSemanticSearchClient
    * knowledge.services.asyncio.base.AsyncServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Methods

    `delete_document_by_id(self, index_mode: Literal['document', 'word'], locale: knowledge.base.language.LocaleCode, document_ids: List[str], auth_key: str | None = None)`
    :   Deletes documents from the index.
        
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

    `force_merge_index(self, index_mode: Literal['document', 'word'], locale: knowledge.base.language.LocaleCode, auth_key: str | None = None) ‑> None`
    :   Force merge the index to optimize storage and performance.
        
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

    `index_health(self, index_mode: Literal['document', 'word'], locale: knowledge.base.language.LocaleCode, auth_key: str | None = None) ‑> knowledge.base.index.HealthResponse`
    :   Checks the health status of an index by sending an asynchronous POST request
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

    `iterate_documents(self, index_mode: Literal['document', 'word'], locale: knowledge.base.language.LocaleCode, auth_key: str | None = None, timeout: int = 60) ‑> AsyncIterator[knowledge.base.index.IndexDocument]`
    :   Stream documents from the index as NDJSON (async version).
        
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

    `refresh_index(self, index_mode: Literal['document', 'word'], locale: knowledge.base.language.LocaleCode, auth_key: str | None = None) ‑> None`
    :   Refresh the index to make recent changes searchable.
        
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