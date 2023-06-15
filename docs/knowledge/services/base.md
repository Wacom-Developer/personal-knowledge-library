Module knowledge.services.base
==============================

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
    verify_calls: bool (Default:= False)
        Flag if  API calls should be verified.

    ### Ancestors (in MRO)

    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Descendants

    * knowledge.nel.base.NamedEntityRecognitionProcessor
    * knowledge.nel.base.PersonalEntityLinkingProcessor
    * knowledge.services.graph.WacomKnowledgeService
    * knowledge.services.group.GroupManagementServiceAPI
    * knowledge.services.ontology.OntologyService
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

    ### Static methods

    `expired(auth_token: str) ‑> bool`
    :   Checks if token is expired.
        
        Parameters
        ----------
        auth_token: str
            Authentication token
        
        Returns
        -------
        expired: bool
            Flag if token is expired

    `expires_in(auth_token: str) ‑> float`
    :   Returns the seconds when the token expires.
        
        Parameters
        ----------
        auth_token: str
            Authentication token
        
        Returns
        -------
        expired_in: float
            Seconds until token is expired

    `unpack_token(auth_token: str) ‑> Dict[str, Any]`
    :   Unpacks the token.
        
        Parameters
        ----------
        auth_token: str
            Authentication token
        
        Returns
        -------
        token_dict: Dict[str, Any]
            Token dictionary

    ### Instance variables

    `application_name`
    :   Application name.

    `auth_endpoint: str`
    :   Authentication endpoint.

    `service_base_url`
    :   Service endpoint.

    `service_endpoint`
    :   Service endpoint.

    ### Methods

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

    `request_user_token(self, tenant_key: str, external_id: str) ‑> Tuple[str, str, datetime.datetime]`
    :   Login as user by using the tenant key and its external user id.
        
        Parameters
        ----------
        tenant_key: str
            Tenant key
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

`WacomServiceException(message: str, status_code: int = 500)`
:   Exception thrown if Wacom service fails.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Instance variables

    `status_code: int`
    :   Status code of the exception.