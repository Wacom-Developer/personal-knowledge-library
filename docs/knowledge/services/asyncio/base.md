Module knowledge.services.asyncio.base
======================================

Variables
---------

`cached_resolver: knowledge.services.asyncio.base.CachedResolver`
:   Cached resolver for aiohttp.

Functions
---------

`cached_getaddrinfo(host: str, *args, **kwargs) ‑> Any`
:   Cached address information.
    
    Parameters
    ----------
    host: str
        Hostname
    args: Any
        Additional arguments
    kwargs: Any
        Additional keyword arguments
    
    Returns
    -------
    addr_info: Any
        Address information

`handle_error(message: str, response: aiohttp.client_reqrep.ClientResponse, parameters: Dict[str, Any] | None = None, payload: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None) ‑> knowledge.services.base.WacomServiceException`
:   Handles an error response.
    
    Parameters
    ----------
    message: str
        Error message
    response: aiohttp.ClientResponse
        Response
    parameters: Optional[Dict[str, Any]] (Default:= None)
        Parameters
    payload: Optional[Dict[str, Any]] (Default:= None)
        Payload
    headers: Optional[Dict[str, str]] (Default:= None)
        Headers
    
    Returns
    -------
    WacomServiceException
        Create exception.

Classes
-------

`AsyncServiceAPIClient(application_name: str = 'Async Knowledge Client', service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph/v1', auth_service_endpoint: str = 'graph/v1', verify_calls: bool = True, timeout: int = 60)`
:   Async Wacom Service API Client
    ------------------------------
    Abstract class for Wacom service APIs.
    
    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    auth_service_endpoint: str (Default:= 'graph/v1')
        Authentication service endpoint
    verify_calls: bool (Default:= True)
        Flag if API calls should be verified.

    ### Ancestors (in MRO)

    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Descendants

    * knowledge.services.asyncio.graph.AsyncWacomKnowledgeService
    * knowledge.services.asyncio.group.AsyncGroupManagementService
    * knowledge.services.asyncio.search.AsyncSemanticSearchClient
    * knowledge.services.asyncio.users.AsyncUserManagementService

    ### Class variables

    `SERVICE_URL: str`
    :   Production service URL

    `STAGING_SERVICE_URL: str`
    :   Staging service URL

    `USER_ENDPOINT: str`
    :

    `USER_LOGIN_ENDPOINT: str`
    :

    `USER_REFRESH_ENDPOINT: str`
    :

    ### Instance variables

    `application_name: str`
    :   Application name.

    `auth_endpoint: str`
    :   Authentication endpoint.

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

    `service_base_url`
    :   Service endpoint.

    `service_endpoint`
    :   Service endpoint.

    `user_agent: str`
    :   User agent.

    ### Methods

    `asyncio_session(self) ‑> aiohttp.client.ClientSession`
    :   Creates and manages an asynchronous HTTP session.
        
        The `session` method ensures that an `aiohttp.ClientSession` is properly created
        and reused for making HTTP requests. It checks whether there's an existing session
        that is closed or uninitialized and re-initializes it if required. Thread safety
        is achieved using an asynchronous lock.
        
        Returns
        -------
        aiohttp.ClientSession
            An instance of aiohttp.ClientSession, either previously created or newly
            instantiated and ready for use in asynchronous operations.

    `close(self)`
    :   Closes the asynchronous session if it is open.
        
        This method ensures that the session is closed in a thread-safe manner. It acquires
        a session lock to prevent concurrent access during the session closure process.
        If the session is already closed, the method will not perform any additional
        operations.

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
    :   Logs out the user from the current session.
        
        This method handles the removal of the current session from the token manager
        and triggers any necessary cleanup operations. If all sessions are terminated,
        it invokes additional resource-closing routines.

    `refresh_token(self, refresh_token: str, timeout: int = 60) ‑> Tuple[str, str, datetime.datetime]`
    :   Refreshing a token.
        
        Parameters
        ----------
        refresh_token: str
            Refresh token
        timeout: int = DEFAULT_TIMEOUT
            Timeout for the request in seconds.
        
        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_key: str
            Refresh token
        expiration_time: str
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
            Tenant api key
        external_id: str
            External id.
        timeout: int = DEFAULT_TIMEOUT
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

`CachedResolver()`
:   CachedResolver
    ==============
    Cached resolver for aiohttp.

    ### Ancestors (in MRO)

    * aiohttp.abc.AbstractResolver
    * abc.ABC

    ### Methods

    `close(self) ‑> None`
    :   Release resolver

    `resolve(self, host: str, port: int = 0, family: int = 2)`
    :   Return IP address for given hostname