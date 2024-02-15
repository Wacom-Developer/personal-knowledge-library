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

    
`handle_error(message: str, response: aiohttp.client_reqrep.ClientResponse, parameters: Optional[Dict[str, Any]] = None, payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) ‑> knowledge.services.base.WacomServiceException`
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

`AsyncServiceAPIClient(application_name: str = 'Async Knowledge Client', service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph/v1', auth_service_endpoint: str = 'graph/v1', verify_calls: bool = True)`
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
        Flag if  API calls should be verified.

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

    `current_session: knowledge.services.session.Session`
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
    :   Login as user by using the tenant id and its external user id.
        Parameters
        ----------
        tenant_api_key: str
            Tenant id
        external_user_id: str
            External user id
        Returns
        -------
        session: PermanentSession
            Session. The session is stored in the token manager and the client is using the session id for further
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
        expiration_time: str
            Expiration time
        
        Raises
        ------
        WacomServiceException
            Exception if service returns HTTP error code.

    `register_token(self, auth_key: str, refresh_token: Optional[str] = None) ‑> Union[knowledge.services.session.RefreshableSession, knowledge.services.session.TimedSession]`
    :   Register token.
        Parameters
        ----------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_token: str
            Refresh token
        
        Returns
        -------
        session: Union[RefreshableSession, TimedSession]
            Session. The session is stored in the token manager and the client is using the session id for further
            calls.

    `request_user_token(self, tenant_api_key: str, external_id: str) ‑> Tuple[str, str, datetime.datetime]`
    :   Login as user by using the tenant key and its external user id.
        
        Parameters
        ----------
        tenant_api_key: str
            Tenant api key
        external_id: str
            External id.
        
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
            Exception if service returns HTTP error code.

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