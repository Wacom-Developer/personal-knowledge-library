Module knowledge.services.queue_management
==========================================

Classes
-------

`QueueManagementClient(service_url: str, application_name: str = 'Queue Management Client', base_auth_url: str | None = None, service_endpoint: str = 'vector/api/v1', verify_calls: bool = True, max_retries: int = 3, backoff_factor: float = 0.1)`
:   QueueManagementClient
    ---------------------
    
    Handles interactions with the queue management portion of the semantic
    search service. The client offers methods to query queue metadata,
    such as names, sizes, and emptiness status, while delegating
    authentication and request handling to the underlying
    WacomServiceAPIClient base class.
    
    Parameters
    ----------
    service_url: str
        URL of the service.
    application_name: str
        Name of the application
    service_endpoint: str
        Base endpoint
    verify_calls: bool (Default:= True)
        Verify API calls.
    max_retries: int (Default:= 3)
        Maximum number of retries for failed requests.
    backoff_factor: float (Default:= 0.3)
        Backoff factor between retries.

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Methods

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