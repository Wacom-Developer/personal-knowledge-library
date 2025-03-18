Module knowledge.services.search
================================

Classes
-------

`SemanticSearchClient(service_url: str, service_endpoint: str = 'vector/api/v1')`
:   Semantic Search Client
    ======================
    Client for searching semantically similar documents and labels.
    
    Parameters
    ----------
    service_url: str
        Service URL for the client.
    service_endpoint: str (Default:= 'vector/v1')
        Service endpoint for the client.

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Methods

    `count_documents(self, locale: knowledge.base.language.LocaleCode, concept_type: str | None = None, auth_key: str | None = None, max_retries: int = 3, backoff_factor: float = 0.1) ‑> int`
    :   Count all documents for a tenant.
        
        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        
        Returns
        -------
        number_of_docs: int
            Number of documents.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `count_documents_filter(self, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any], auth_key: str | None = None, max_retries: int = 3, backoff_factor: float = 0.1) ‑> int`
    :   Count all documents for a tenant with filters.
        
        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        
        Returns
        -------
        number_of_docs: int
            Number of documents.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `count_labels(self, locale: knowledge.base.language.LocaleCode, concept_type: str | None = None, auth_key: str | None = None, max_retries: int = 3, backoff_factor: float = 0.1) ‑> int`
    :   Count all labels entries for a tenant.
        
        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        concept_type: Optional[str] (Default:= None)
            Concept type.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If auth key is provided, it will be used for the request.
        Returns
        -------
        count: int
            Number of words.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `count_labels_filter(self, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any], auth_key: str | None = None, max_retries: int = 3, backoff_factor: float = 0.1) ‑> int`
    :   Count all labels for a tenant with filters.
        
        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        
        Returns
        -------
        number_of_docs: int
            Number of labels.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `document_search(self, query: str, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any] | None = None, max_results: int = 10, max_retries: int = 3, backoff_factor: float = 0.1, auth_key: str | None = None) ‑> knowledge.base.search.DocumentSearchResponse`
    :   Async Semantic search.
        
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
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        search_results: DocumentSearchResponse
            Search results response.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `labels_search(self, query: str, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any] | None = None, max_results: int = 10, max_retries: int = 3, backoff_factor: float = 0.1, auth_key: str | None = None) ‑> knowledge.base.search.LabelMatchingResponse`
    :   Async search for semantically similar labels.
        
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
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        list_entities: Dict[str, Any]
            Search results response.

    `retrieve_documents_chunks(self, locale: knowledge.base.language.LocaleCode, uri: str, max_retries: int = 3, backoff_factor: float = 0.1, auth_key: str | None = None) ‑> List[knowledge.base.search.VectorDBDocument]`
    :   Retrieve document chunks from vector database. The service is automatically chunking the document into
        smaller parts. The chunks are returned as a list of dictionaries, with metadata and content.
        
        Parameters
        ----------
        locale: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        uri: str
            URI of the document
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        document: List[VectorDBDocument]:
            List of document chunks with metadata and content related to the document.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `retrieve_labels(self, locale: knowledge.base.language.LocaleCode, uri: str, max_retries: int = 3, backoff_factor: float = 0.1, auth_key: str | None = None) ‑> List[knowledge.base.search.VectorDBDocument]`
    :   Retrieve labels from vector database.
        
        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        document: List[VectorDBDocument]
            List of labels with metadata and content related to the entity with uri.
        
        Raises
        ------
        WacomServiceException
            If the request fails.