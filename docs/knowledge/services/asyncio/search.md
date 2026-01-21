Module knowledge.services.asyncio.search
========================================

Classes
-------

`AsyncSemanticSearchClient(service_url: str, application_name: str = 'Async Semantic Search ', base_auth_url: str | None = None, service_endpoint: str = 'vector/api/v1', verify_calls: bool = True, timeout: int = 60)`
:   Semantic Search Client
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

    ### Ancestors (in MRO)

    * knowledge.services.asyncio.base.AsyncServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Methods

    `count_documents(self, locale: knowledge.base.language.LocaleCode, concept_type: str | None = None, auth_key: str | None = None, timeout: int = 60) ‑> int`
    :   Count all documents for a tenant.
        
        Parameters
        ----------
        locale: str
            Locale
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
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

    `count_documents_filter(self, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any], auth_key: str | None = None, timeout: int = 60) ‑> int`
    :   Count all documents for a tenant using a filter.
        
        Parameters
        ----------
        locale: str
            Locale
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
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

    `count_labels(self, locale: str, concept_type: str | None = None, auth_key: str | None = None, timeout: int = 60) ‑> int`
    :   Count all labels entries for a tenant.
        
        Parameters
        ----------
        locale: str
            Locale
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If an auth key is provided, it will be used for the request.
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

    `count_labels_filter(self, locale: knowledge.base.language.LocaleCode, filters: Dict[str, Any], auth_key: str | None = None, timeout: int = 60) ‑> int`
    :   Count all labels for a tenant using a filter.
        
        Parameters
        ----------
        locale: str
            Locale
        filters: Dict[str, Any]
            Filters for the search
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
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

    `document_search(self, query: str, locale: str, filters: Dict[str, Any] | None = None, max_results: int = 10, filter_mode: Literal['AND', 'OR'] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> knowledge.base.search.DocumentSearchResponse`
    :   Async Semantic search.
        
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
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
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

    `filter_documents(self, locale: str, filters: Dict[str, Any] | None = None, filter_mode: Literal['AND', 'OR'] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> knowledge.base.search.FilterVectorDocumentsResponse`
    :   Filters documents based on the provided criteria, locale, and other optional
        parameters. This method sends an asynchronous POST request to the filtering
        endpoint, allowing users to retrieve filtered documents.
        
        Parameters
        ----------
        locale : str
            The locale against which the filtering operation is performed.
        
        filters : Optional[Dict[str, Any]], default=None
            A dictionary of filters that define the criteria for document filtering.
            If not provided, the default is an empty dictionary.
        
        filter_mode : Optional[Literal["AND", "OR"]], default=None
            Specifies the filter mode to apply: "AND" for matching all filter criteria
            or "OR" for matching any of the criteria. If not provided, the default is
            None, which may use a predefined behavior.
        
        auth_key : Optional[str], default=None
            An optional authentication key to override the default authorization token
            for this specific request.
        
        timeout : int, default=DEFAULT_TIMEOUT
            The maximum duration in seconds to wait for the filtering operation before
            a timeout is triggered.
        
        Returns
        -------
        FilterVectorDocumentsResponse
            The response object containing the filtered documents and any related
            metadata.
        
        Raises
        ------
        Exception
            If the filtering operation fails or the server returns an error status code.

    `filter_labels(self, locale: str, filters: Dict[str, Any] | None = None, filter_mode: Literal['AND', 'OR'] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> knowledge.base.search.FilterVectorDocumentsResponse`
    :   Filters labels based on the provided criteria, locale, and other optional
        parameters. This method sends an asynchronous POST request to the filtering
        endpoint, allowing users to retrieve filtered documents.
        
        Parameters
        ----------
        locale : str
            The locale against which the filtering operation is performed.
        
        filters : Optional[Dict[str, Any]], default=None
            A dictionary of filters that define the criteria for document filtering.
            If not provided, the default is an empty dictionary.
        
        filter_mode : Optional[Literal["AND", "OR"]], default=None
            Specifies the filter mode to apply: "AND" for matching all filter criteria
            or "OR" for matching any of the criteria. If not provided, the default is
            None, which may use a predefined behavior.
        
        auth_key : Optional[str], default=None
            An optional authentication key to override the default authorization token
            for this specific request.
        
        timeout : int, default=DEFAULT_TIMEOUT
            The maximum duration in seconds to wait for the filtering operation before
            a timeout is triggered.
        
        Returns
        -------
        FilterVectorDocumentsResponse
            The response object containing the filtered documents and any related
            metadata.
        
        Raises
        ------
        Exception
            If the filtering operation fails or the server returns an error status code.

    `labels_search(self, query: str, locale: str, filters: Dict[str, Any] | None = None, max_results: int = 10, filter_mode: Literal['AND', 'OR'] | None = None, auth_key: str | None = None, timeout: int = 60) ‑> knowledge.base.search.LabelMatchingResponse`
    :   Async search for semantically similar labels.
        
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
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (default: 60 seconds).
        Returns
        -------
        response: LabelMatchingResponse
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
        queue management endpoint. The method interacts with a remote API, using prepared
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

    `retrieve_document_chunks(self, locale: knowledge.base.language.LocaleCode, uri: str, auth_key: str | None = None, timeout: int = 60) ‑> List[knowledge.base.search.VectorDBDocument]`
    :   Retrieve document chunks from a vector database. The service is automatically chunking the document into
        smaller parts. The chunks are returned as a list of dictionaries, with metadata and content.
        
        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
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

    `retrieve_labels(self, locale: knowledge.base.language.LocaleCode, uri: str, auth_key: str | None = None, timeout: int = 60) ‑> List[knowledge.base.search.VectorDBDocument]`
    :   Retrieve labels from a vector database.
        
        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
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