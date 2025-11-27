Module knowledge.services.search
================================

Classes
-------

`SemanticSearchClient(service_url: str, application_name: str = 'Semantic Search Client', base_auth_url: str | None = None, service_endpoint: str = 'vector/api/v1', verify_calls: bool = True, max_retries: int = 3, backoff_factor: float = 0.1)`
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

    `count_documents(self, locale: knowledge.base.language.LocaleCode, concept_type: str | None = None, auth_key: str | None = None, timeout: int = 60) ‑> int`
    :   Count all documents for a tenant.
        
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

    `count_documents_filter(self, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any], auth_key: str | None = None, timeout: int = 60) ‑> int`
    :   Count all documents for a tenant with filters.
        
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

    `count_labels(self, locale: knowledge.base.language.LocaleCode, concept_type: str | None = None, auth_key: str | None = None, timeout: float = 60) ‑> int`
    :   Count all labels entries for a tenant.
        
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

    `count_labels_filter(self, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any], auth_key: str | None = None, timeout: int = 60) ‑> int`
    :   Count all labels for a tenant with filters.
        
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

    `document_search(self, query: str, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any] | None = None, max_results: int = 10, filter_mode: Literal['AND', 'OR'] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> knowledge.base.search.DocumentSearchResponse`
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

    `labels_search(self, query: str, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any] | None = None, filter_mode: Literal['AND', 'OR'] | None = None, max_results: int = 10, auth_key: str | None = None, timeout: int = 60) ‑> knowledge.base.search.LabelMatchingResponse`
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

    `list_queue_names(self, auth_key: str | None = None) ‑> knowledge.base.queue.QueueNames`
    :   List all available queues in the semantic search service.
        
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

    `list_queues(self, auth_key: str | None = None) ‑> List[knowledge.base.queue.QueueMonitor]`
    :   Parameters
        ----------
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        queues: List[QueueMonitor]
            List of queues.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `queue_is_empty(self, queue_name: str, auth_key: str | None = None) ‑> bool`
    :   Checks if a given queue is empty.
        
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

    `queue_monitor_information(self, queue_name: str, auth_key: str | None = None) ‑> knowledge.base.queue.QueueMonitor`
    :   Gets the monitoring information for a specific queue.
        
        Parameters
        ----------
        queue_name : str
            The name of the queue for which monitoring information is requested.
        auth_key : Optional[str], optional
            An optional authentication key to be used for the request. If not provided,
            an internal token will be fetched and used.
        
        Returns
        -------
        QueueMonitor
            A parsed representation of the queue monitoring information.
        
        Raises
        ------
        Exception
            Raised if the request fails or if there is an issue with fetching the
            monitoring data. Details of the failure are included.

    `queue_size(self, queue_name: str, auth_key: str | None = None) ‑> knowledge.base.queue.QueueCount`
    :   Gets the size of a specified queue by making an asynchronous request to the service's
        queue management endpoint. The method interacts with a remote API, utilizing prepared
        headers and query parameters, and parses the returned data into the appropriate
        response structure upon a successful response.
        
        Parameters
        ----------
        queue_name : str
            The name of the queue whose size is being retrieved.
        auth_key : Optional[str], optional
            An optional authentication key to overwrite the default one when preparing headers.
        
        Returns
        -------
        QueueCount
            The parsed response encapsulating the size and additional metadata of the specified
            queue.
        
        Raises
        ------
        Exception
            If the API request fails, an error is raised with the relevant information.

    `retrieve_documents_chunks(self, locale: knowledge.base.language.LocaleCode, uri: str, auth_key: str | None = None, timeout: int = 60) ‑> List[knowledge.base.search.VectorDBDocument]`
    :   Retrieve document chunks from the vector index. The service is automatically chunking the document into
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

    `retrieve_labels(self, locale: knowledge.base.language.LocaleCode, uri: str, auth_key: str | None = None, timeout: int = 60) ‑> List[knowledge.base.search.VectorDBDocument]`
    :   Retrieve labels from the vector index.
        
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