Module knowledge.services.index_management
==========================================

Classes
-------

`IndexManagementClient(service_url: str, application_name: str = 'Index Management Client', base_auth_url: str | None = None, service_endpoint: str = 'vector/api/v1', verify_calls: bool = True, max_retries: int = 3, backoff_factor: float = 0.1)`
:   Index Management Client
    ========================
    Client for searching managing the index.
    
    Parameters
    ----------
    service_url: str
        Service URL for the client.
    service_endpoint: str (Default:= 'vector/v1')
        Service endpoint for the client.

    ### Ancestors (in MRO)

    * knowledge.services.search.SemanticSearchClient
    * knowledge.services.base.WacomServiceAPIClient
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
    :   Checks the health status of an index by sending an asynchronous GET request
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

    `iterate_documents(self, index_mode: Literal['document', 'word'], locale: knowledge.base.language.LocaleCode, auth_key: str | None = None, timeout: int = 60) ‑> Iterator[knowledge.base.index.IndexDocument]`
    :   Stream documents from the index as NDJSON.
        
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