Module knowledge.services.asyncio.base
======================================

Functions
---------

`cached_getaddrinfo(host: str, *args: Any, **kwargs: Any) ‑> Any`
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

`handle_error(message: str, response: knowledge.services.asyncio.base.ResponseData, parameters: Dict[str, Any] | None = None, payload: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None) ‑> knowledge.services.base.WacomServiceException`
:   Handles an error response.
    
    Parameters
    ----------
    message: str
        Error message
    response: ResponseData
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

`AsyncServiceAPIClient(service_url: str, application_name: str = 'Async Knowledge Client', base_auth_url: str | None = None, service_endpoint: str = 'graph/v1', verify_calls: bool = True, timeout: int = 60)`
:   Async Wacom Service API Client
    ------------------------------
    Abstract class for Wacom service APIs.
    
    Parameters
    ----------
    service_url: str
        URL of the service
    base_auth_url: Optional[str] (Default:= None)
        Authentication URL for local development
    service_endpoint: str
        Base endpoint for the service
    verify_calls: bool (Default:= True)
        Flag if API calls should be verified.
    timeout: int (Default:= DEFAULT_TIMEOUT)
        Timeout for the request in seconds.

    ### Ancestors (in MRO)

    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Descendants

    * knowledge.services.asyncio.graph.AsyncWacomKnowledgeService
    * knowledge.services.asyncio.group.AsyncGroupManagementService
    * knowledge.services.asyncio.ink.AsyncInkServices
    * knowledge.services.asyncio.queue_management.AsyncQueueMonitorClient
    * knowledge.services.asyncio.search.AsyncSemanticSearchClient
    * knowledge.services.asyncio.users.AsyncUserManagementService

    ### Class variables

    `USER_ENDPOINT: str`
    :   The type of the None singleton.

    `USER_LOGIN_ENDPOINT: str`
    :   The type of the None singleton.

    `USER_REFRESH_ENDPOINT: str`
    :   The type of the None singleton.

    ### Instance variables

    `application_name: str`
    :   Application name.

    `auth_endpoint: str`
    :   Authentication endpoint.

    `base_auth_url: str`
    :   Base authentication URL.

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

    `service_base_url: str`
    :   Service endpoint.

    `service_endpoint: str`
    :   Service endpoint.

    `user_agent: str`
    :   User agent.

    ### Methods

    `asyncio_session(self) ‑> knowledge.services.asyncio.base.AsyncSession`
    :   Returns an asynchronous session.
        
        Returns
        -------
        session: AsyncSession
            Asynchronous session

    `close(self) ‑> None`
    :   Closes the asynchronous session if it is open.
        
        This method ensures that the session is closed in a thread-safe manner. It acquires
        a session lock to prevent concurrent access during the session closure process.
        If the session is already closed, the method will not perform any additional
        operations.

    `handle_token(self, force_refresh: bool = False, force_refresh_timeout: float = 120) ‑> Tuple[str, str | None]`
    :   Handles the token and refreshes it if needed.
        
        Parameters
        ----------
        force_refresh: bool
            Force refresh token
        force_refresh_timeout: float
            Force refresh timeout in seconds
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

    `logout(self) ‑> None`
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

    `use_session(self, session_id: str) ‑> None`
    :   Use session.
        Parameters
        ----------
        session_id: str
            Session id

`AsyncSession(client: AsyncServiceAPIClient, timeout: int = 60)`
:   Represents an asynchronous session manager for making HTTP requests.
    
    The `AsyncSession` class is designed to handle and manage asynchronous HTTP
    requests using the `aiohttp` library. It manages session creation,
    handles headers, manages authentication, and supports multiple HTTP methods
    (GET, POST, PUT, DELETE, PATCH). It is intended to simplify structured
    HTTP requests in an asynchronous context.
    
    Parameters
    ----------
    client: AsyncServiceAPIClient
        The client instance.
    timeout: int
        The default timeout duration in seconds for requests.

    ### Methods

    `close(self) ‑> None`
    :   Closes the existing session asynchronously.
        
        This method ensures that the session is properly closed and reset to `None`.
        It acquires a session lock to guarantee thread-safe operations.
        
        Notes
        -----
        It is essential to invoke this method to release system resources
        associated with the session.
        
        Raises
        ------
        Exception
            If an error occurs during the session closure operation.

    `delete(self, url: str, **kwargs: Any) ‑> knowledge.services.asyncio.base.ResponseData`
    :   Asynchronously performs an HTTP DELETE request.
        
        This method sends a DELETE request to the specified URL with additional
        optional parameters provided as keyword arguments. It utilizes the
        `request` method internally for executing the DELETE operation.
        
        Parameters
        ----------
        url : str
            The URL to which the DELETE request should be sent.
        **kwargs
            Optional parameters to include in the DELETE request, such as
            headers, data, or additional request configurations.
        
        Returns
        -------
        ResponseData
            The response object resulting from the DELETE request. This
            provides access to the response data, status, and headers.

    `get(self, url: str, **kwargs: Any) ‑> knowledge.services.asyncio.base.ResponseData`
    :   Asynchronously sends an HTTP GET request to the specified URL.
        
        This method allows sending GET requests with optional additional parameters
        passed through `kwargs`. It leverages the `request` method to handle the
        operation and returns the corresponding response.
        
        Parameters
        ----------
        url : str
            The target URL for the HTTP GET request.
        **kwargs
            Additional keyword arguments to configure the GET request. These may
            include headers, query parameters, or other request-specific options.
        
        Returns
        -------
        ResponseData
            The response object resulting from the get-go request, containing status,
            headers, and body data.

    `patch(self, url: str, **kwargs: Any) ‑> knowledge.services.asyncio.base.ResponseData`
    :   Asynchronously sends an HTTP PATCH request to the specified URL.
        
        This method is a coroutine that simplifies sending PATCH requests
        using the underlying `request` method. It allows adding additional
        parameters such as headers, data, or query parameters to the request,
        passed via `**kwargs`. The response is returned as an instance of
        `ResponseData`.
        
        Parameters
        ----------
        url : str
            The target URL for the HTTP PATCH request.
        **kwargs
            Additional request parameters like headers, data, or query parameters.
        
        Returns
        -------
        ResponseData
            The response object resulting from the PATCH request, which provides
            methods for accessing the content, status, and headers of the HTTP
            response.

    `post(self, url: str, **kwargs: Any) ‑> knowledge.services.asyncio.base.ResponseData`
    :   Sends an asynchronous HTTP POST request to the specified URL with the given parameters.
        
        This method uses the underlying `request` method to perform the HTTP POST
        operation. Any additional keyword arguments provided will be forwarded
        to the `request` method for customization of the request. Returns the
        response object resulting from the POST operation.
        
        Parameters
        ----------
        url : str
            The URL to which the POST request will be sent.
        **kwargs
            Arbitrary keyword arguments that will be passed to the `request`
            method, allowing customization of the request (e.g., headers,
            json data, params).
        
        Returns
        -------
        ResponseData
            Represents the response object from the POST request.

    `put(self, url: str, **kwargs: Any) ‑> knowledge.services.asyncio.base.ResponseData`
    :   Asynchronously performs an HTTP PUT request.
        
        The method sends an HTTP PUT request to the specified URL with the given
        arguments. Typically used to update or create data at the target URL.
        
        Parameters
        ----------
        url : str
            The URL to which the PUT request is sent.
        **kwargs : dict
            Additional request parameters passed to the underlying request method.
        
        Returns
        -------
        ResponseData
            The response object returned after the PUT request is completed.

    `request(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], url: str, headers: Dict[str, str] | None = None, **kwargs: Any) ‑> knowledge.services.asyncio.base.ResponseData`
    :   Executes an HTTP request using the specified method, URL, headers, and additional options.
        
        Parameters
        ----------
        method : HTTPMethodFunction
            The HTTP method to execute (e.g., "GET", "POST", "PUT", "DELETE", or "PATCH").
        url : str
            The URL to which the request should be sent.
        headers : Optional[Dict[str, str]]
            Headers to include in the request. Defaults to None.
        kwargs : dict
            Additional arguments to pass to the request method of aiohttp.ClientSession.
        
        Returns
        -------
        ResponseData
            The response object resulting from the HTTP request.
        
        Raises
        ------
        ValueError
            If the specified HTTP method is unsupported.

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

    `resolve(self, host: str, port: int = 0, family: int = 2) ‑> List[Dict[str, Any]]`
    :   Resolves a hostname to a list of address information. This is an asynchronous
        method that fetches the address details for the given hostname. The result
        includes protocol, host address, port, and family information. The family
        parameter defaults to IPv4.
        
        Parameters
        ----------
        host : str
            The hostname or IP address to be resolved.
        port : int, optional
            The port number to include in the resolved information. Defaults to 0.
        family : int, optional
            The address family to use for the resolution. Defaults to socket.AF_INET.
        
        Returns
        -------
        list of dict
            A list of dictionaries containing resolved address information, including
            - `hostname`: The original host input.
            - `host`: The resolved host address.
            - `port`: The port number.
            - `family`: The address family used for resolution.
            - `proto`: Protocol number, set to 0.
            - `flags`: Address information flags, set to socket.AI_NUMERICHOST.

`ResponseData(ok: bool, status: int, content: str | bytes | bool | Dict[str, Any] | List[Any], url: str, method: str)`
:   Represents the data returned from an HTTP request.
    
    The ResponseData dataclass encapsulates the response from an HTTP
    call by storing whether the call succeeded, the status code
    received, and the raw content of the response. It is used by
    client code to distinguish between successful and failed
    requests and to access the payload returned by the server.
    
    Attributes
    ----------
    ok: bool
        Boolean flag indicating success of the request.
    status: str
        Numeric status code returned by the server.
    content: Union[str, bytes, bool, Dict[str, Any], List[Any]]
        Raw payload returned in the response body.
    url: str
        URL of the request.
    method: str
        Request method.

    ### Instance variables

    `content: str | bytes | bool | Dict[str, Any] | List[Any]`
    :   The type of the None singleton.

    `method: str`
    :   The type of the None singleton.

    `ok: bool`
    :   The type of the None singleton.

    `status: int`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.