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

`WacomServiceAPIClient(application_name: str, service_url: str, service_endpoint: str, verify_calls: bool = True)`
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

    `AUTH_ENDPOINT: str`
    :

    `USER_ENDPOINT: str`
    :

    `USER_LOGIN_ENDPOINT: str`
    :

    ### Instance variables

    `application_name`
    :   Application name.

    `service_base_url`
    :   Service endpoint.

    `service_endpoint`
    :   Service endpoint.

    ### Methods

    `request_user_token(self, tenant_key: str, external_id: str) ‑> str`
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
        
        Raises
        ------
        WacomServiceException
            Exception if service returns HTTP error code.

`WacomServiceException(*args, **kwargs)`
:   Exception thrown if Wacom service fails.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException