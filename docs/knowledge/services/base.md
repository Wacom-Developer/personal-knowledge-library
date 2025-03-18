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

`WacomServiceAPIClient(application_name: str, service_url: str, service_endpoint: str, auth_service_endpoint: str = 'graph/v1', verify_calls: bool = True)`
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
    auth_service_endpoint: str (Default:= 'graph/v1')
        Authentication service endpoint
    verify_calls: bool (Default:= True)
        Flag if  API calls should be verified.

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

    `application_name`
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

    `register_token(self, auth_key: str, refresh_token: str | None = None) ‑> knowledge.services.session.RefreshableSession | knowledge.services.session.TimedSession`
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
            Tenant API key
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
    
    Attributes
    ----------
    headers: Optional[Dict[str, Any]]
        Headers of the exception
    method: Optional[str]
        Method of the exception
    params: Optional[Dict[str, Any]]
        Parameters of the exception
    payload: Optional[Dict[str, Any]]
        Payload of the exception
    url: Optional[str]
        URL of the exception
    message: str
        Message of the exception
    status_code: int
        Status code of the exception

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

    `service_response: requests.models.Response | None`
    :   Service response.

    `status_code: int`
    :   Status code of the exception.

    `url: str | None`
    :   URL of the exception.