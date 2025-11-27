Module knowledge.services.base
==============================

Functions
---------

`format_exception(exception: knowledge.services.base.WacomServiceException) ‑> str`
:   Formats the exception.
    
    Parameters
    ----------
    exception: WacomServiceException
        Exception
    
    Returns
    -------
    formatted_exception: str
        Formatted exception

`handle_error(message: str, response: requests.models.Response, parameters: Dict[str, Any] | None = None, payload: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None) ‑> knowledge.services.base.WacomServiceException`
:   Handles an error response.
    
    Parameters
    ----------
    message: str
        Error message
    response: Response
        Response from the service
    parameters: Optional[Dict[str, Any]] (Default:= None)
        Parameters
    payload: Optional[Dict[str, Any]] (Default:= None)
        Payload
    headers: Optional[Dict[str, str]] (Default:= None)
        Headers
    
    Returns
    -------
    WacomServiceException
        Returns the generated exception.

Classes
-------

`RESTAPIClient(service_url: str, verify_calls: bool = False)`
:   Abstract REST API client
    ------------------------
    REST API client handling the service url.
    
    Arguments
    ---------
    service_url: str
        Service URL for service
    verify_calls: bool (default:= False)
        Flag if the service calls should be verified

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.nel.base.PublicEntityLinkingProcessor
    * knowledge.services.asyncio.base.AsyncServiceAPIClient
    * knowledge.services.base.WacomServiceAPIClient

    ### Instance variables

    `service_url: str`
    :   Service URL.

    `verify_calls`
    :   Certificate verification activated.

`RequestsSession(client: WacomServiceAPIClient, pool_connections: int = 10, pool_maxsize: int = 10, max_retries: int = 3, backoff_factor: float = 0.3)`
:   Reusable requests session with automatic token management.
    
    This session wrapper provides connection pooling, automatic token refresh,
    and proper cleanup of resources.
    
    Parameters
    ----------
    client: WacomServiceAPIClient
        The API client instance
    pool_connections: int (Default:= 10)
        Number of connection pools to cache
    pool_maxsize: int (Default:= 10)
        Maximum number of connections to save in the pool
    max_retries: int (Default:= 3)
        Maximum number of retries for failed requests

    ### Instance variables

    `backoff_factor: float`
    :   Backoff factor for failed requests.

    `max_retries: int`
    :   Maximum number of retries for failed requests.

    `pool_connections: int`
    :   Number of connection pools to cache.

    `pool_maxsize: int`
    :   Maximum number of connections to save in the pool.

    ### Methods

    `close(self)`
    :   Close the session and release resources.

    `delete(self, url: str, **kwargs) ‑> requests.models.Response`
    :   Execute a DELETE request.
        
        Parameters
        ----------
        url: str
            URL for the request.
        kwargs: Dict[str, Any] (Default:= {})
            Additional arguments for the request.
        
        Returns
        -------
        response: Response
            Response from the service.

    `get(self, url: str, **kwargs) ‑> requests.models.Response`
    :   Execute GET request.
        
        Parameters
        ----------
        url: str
            URL for the request.
        kwargs: Dict[str, Any] (Default:= {})
            Additional arguments for the request.
        
        Returns
        -------
        response: Response
            Response from the service.

    `patch(self, url: str, **kwargs) ‑> requests.models.Response`
    :   Execute a PATCH request.
        
        Parameters
        ----------
        url: str
            URL for the request.
        kwargs: Dict[str, Any] (Default:= {})
            Additional arguments for the request.
        
        Returns
        -------
        response: Response
            Response from the service.

    `post(self, url: str, **kwargs) ‑> requests.models.Response`
    :   Execute POST request.
        
        Parameters
        ----------
        url: str
            URL for the request.
        kwargs: Dict[str, Any] (Default:= {})
            Additional arguments for the request.
        
        Returns
        -------
        response: Response
            Response from the service.

    `put(self, url: str, **kwargs) ‑> requests.models.Response`
    :   Execute a PUT request.
        
        Parameters
        ----------
        url: str
            URL for the request.
        kwargs: Dict[str, Any] (Default:= {})
            Additional arguments for the request.
        
        Returns
        -------
        response: Response
            Response from the service.

    `request(self, method: str, url: str, headers: Dict[str, str] | None = None, timeout: int = 60, **kwargs) ‑> requests.models.Response`
    :   Execute a request with automatic token handling.

`WacomServiceAPIClient(service_url: str, application_name: str = 'Knowledge Client', base_auth_url: str | None = None, service_endpoint: str = 'graph/v1', verify_calls: bool = True, max_retries: int = 3, backoff_factor: float = 0.1)`
:   Wacom Service API Client
    ------------------------
    Abstract class for Wacom service APIs.
    
    Parameters
    ----------
    application_name: str
        Name of the application using the service
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    verify_calls: bool (Default:= True)
        Flag if API calls should be verified.

    ### Ancestors (in MRO)

    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Descendants

    * knowledge.nel.base.NamedEntityRecognitionProcessor
    * knowledge.nel.base.PersonalEntityLinkingProcessor
    * knowledge.services.graph.WacomKnowledgeService
    * knowledge.services.group.GroupManagementService
    * knowledge.services.ontology.OntologyService
    * knowledge.services.search.SemanticSearchClient
    * knowledge.services.tenant.TenantManagementServiceAPI
    * knowledge.services.users.UserManagementServiceAPI

    ### Class variables

    `USER_ENDPOINT: str`
    :

    `USER_LOGIN_ENDPOINT: str`
    :

    `USER_REFRESH_ENDPOINT: str`
    :

    ### Instance variables

    `application_name`
    :   Application name.

    `auth_endpoint: str`
    :   Authentication endpoint.

    `base_auth_url`
    :   Base authentication endpoint.

    `current_session: knowledge.services.session.RefreshableSession | knowledge.services.session.TimedSession | knowledge.services.session.PermanentSession | None`
    :   Current session.
        
        Returns
        -------
        session: Union[TimedSession, RefreshableSession, PermanentSession]
            Current session
        
        Raises
        ------
        WacomServiceException
            Exception if no session is available.

    `request_session: knowledge.services.base.RequestsSession`
    :   Request session.

    `service_base_url`
    :   Service endpoint.

    `service_endpoint`
    :   Service endpoint.

    `token_manager: knowledge.services.session.TokenManager`
    :   Token manager.

    `user_agent: str`
    :   User agent.

    ### Methods

    `handle_token(self, force_refresh: bool = False, force_refresh_timeout: float = 120) ‑> Tuple[str, str]`
    :   Handles the token and refreshes it if needed.
        
        Parameters
        ----------
        force_refresh: bool
            Force refresh token
        force_refresh_timeout: int
            Force refresh timeout
        Returns
        -------
        user_token: str
            The user token
        refresh_token: str
            The refresh token

    `login(self, tenant_api_key: str, external_user_id: str) ‑> knowledge.services.session.PermanentSession`
    :   Login as a user by using the tenant id and its external user id.
        Parameters
        ----------
        tenant_api_key: str
            Tenant id
        external_user_id: str
            External user id
        Returns
        -------
        session: PermanentSession
            Session. The session is stored in the token manager, and the client is using the session id for further
            calls.

    `logout(self)`
    :   Logout user.

    `refresh_token(self, refresh_token: str) ‑> Tuple[str, str, datetime.datetime]`
    :   Refreshing a token.
        
        Parameters
        ----------
        refresh_token: str
            Refresh token
        
        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_key: str
            Refresh token
        expiration_time: datetime
            Expiration time
        
        Raises
        ------
        WacomServiceException
            Exception if the service returns HTTP error code.

    `register_token(self, auth_key: str, refresh_token: str | None = None) ‑> knowledge.services.session.RefreshableSession | knowledge.services.session.TimedSession`
    :   Register a token.
        Parameters
        ----------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_token: str
            Refresh token
        
        Returns
        -------
        session: Union[RefreshableSession, TimedSession]
            Session. The session is stored in the token manager, and the client is using the session id for further
            calls.

    `request_user_token(self, tenant_api_key: str, external_id: str, timeout: int = 60) ‑> Tuple[str, str, datetime.datetime]`
    :   Login as a user by using the tenant key and its external user id.
        
        Parameters
        ----------
        tenant_api_key: str
            Tenant API key
        external_id: str
            External id.
        timeout: int (Default:= DEFAULT_TIMEOUT)
            Timeout for the request in seconds.
        
        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_key: str
            Refresh token
        expiration_time: datatime
            Expiration time
        
        Raises
        ------
        WacomServiceException
            Exception if the service returns HTTP error code.

    `use_session(self, session_id: str)`
    :   Use session.
        Parameters
        ----------
        session_id: str
            Session id

`WacomServiceException(message: str, headers: Dict[str, Any] | None = None, payload: Dict[str, Any] | None = None, params: Dict[str, Any] | None = None, method: str | None = None, url: str | None = None, service_response: str | None = None, status_code: int = 500)`
:   Exception thrown if Wacom service fails.
    
    Parameters
    ----------
    message: str
        Error message
    payload: Optional[Dict[str, Any]] (Default:= None)
        Payload
    params: Optional[Dict[str, Any]] (Default:= None)
        Parameters
    method: Optional[str] (Default:= None)
        Method
    url: Optional[str] (Default:= None)
        URL
    service_response: Optional[str] (Default:= None)
        Service response
    status_code: int (Default:= 500)
        Status code

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `headers: Dict[str, Any] | None`
    :   Headers of the exception.

    `message: str`
    :   Message of the exception.

    `method: str | None`
    :   Method of the exception.

    `params: Dict[str, Any] | None`
    :   Parameters of the exception.

    `payload: Dict[str, Any] | None`
    :   Payload of the exception.

    `service_response: str | None`
    :   Service response.

    `status_code: int`
    :   Status code of the exception.

    `url: str | None`
    :   URL of the exception.