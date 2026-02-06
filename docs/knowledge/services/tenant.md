Module knowledge.services.tenant
================================

Classes
-------

`TenantManagementServiceAPI(tenant_token: str, service_url: str, application_name: str = 'Tenant Manager Client', base_auth_url: str | None = None, service_endpoint: str = 'graph/v1', verify_calls: bool = True, max_retries: int = 3, backoff_factor: float = 0.1)`
:   Handles tenant management services by interacting with a Wacom API client.
    
    This class provides functionalities to create, list, update, and delete tenants.
    It extends the `WacomServiceAPIClient` base class, leveraging its shared capabilities
    to interact with the API endpoints.
    
    Parameters
    ----------
    tenant_token: str
        Tenant Management token.
    service_url: str
        Base URL of the Wacom service.
    application_name: str = "Tenant Manager Client"
        Name of the application using the client.
    base_auth_url: Optional[str] = None
        Base URL of the authentication service.
    service_endpoint: str = "tenant"
        Service endpoint for tenant management.
    verify_calls: bool = True
        Verify API calls.
    max_retries: int = DEFAULT_MAX_RETRIES
        Maximum number of retries for failed requests.
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
        Backoff factor between retries.
    
    
    Attributes
    ----------
    TENANT_ENDPOINT : str
        API endpoint for tenant-related functionalities.
    USER_DETAILS_ENDPOINT : str
        API endpoint for retrieving user details.

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `TENANT_ENDPOINT: str`
    :

    `USER_DETAILS_ENDPOINT: str`
    :

    ### Instance variables

    `tenant_management_token: str`
    :   Tenant Management token.

    ### Methods

    `create_tenant(self, name: str, create_and_apply_onto: bool = True, rights: List[str] | None = None, timeout: int = 60) ‑> Dict[str, str]`
    :   Creates a tenant.
        
        Parameters
        ----------
        name: str -
            Name of the tenant
        create_and_apply_onto: bool
            Creates and applies the ontology.
        rights: List[str]
            List of rights for the tenant. They are encoded in the user token, e.g., "ink-to-text"
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        tenant_dict: Dict[str, str]
            Newly created tenant structure.
            >>>     {
            >>>       "id": "<Tenant-ID>",
            >>>       "apiKey": "<Tenant-API-Key>",
            >>>       "name": "<Tenant-Name>"
            >>>    }
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `delete_tenant(self, identifier: str, timeout: int = 60) ‑> None`
    :   Delete a tenant.
        Parameters
        ----------
        identifier: str
            Tenant identifier.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `listing_tenant(self, timeout: int = 60) ‑> List[knowledge.base.tenant.TenantConfiguration]`
    :   Listing all tenants configured for this instance.
        
        Parameters
        ----------
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        tenants:  List[TenantConfiguration]
            List of tenants
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `update_tenant_configuration(self, identifier: str, rights: List[str], vector_search_data_properties: List[str], vector_search_object_properties: List[str], content_data_property_name: str, timeout: int = 60) ‑> None`
    :   Update the configuration of a tenant.
        
        Parameters
        ----------
        identifier: str
            Tenant identifier.
        rights: List[str]
            List of rights for the tenant. They are encoded in the user token, e.g., "ink-to-text"
        vector_search_data_properties: List[str]
            List of data properties that are automatically added to meta-data of the vector search index documents.
        vector_search_object_properties: List[str]
            List of object properties that are automatically added to meta-data of the vector search index documents.
        content_data_property_name: str
            The data property that is used to indexing its content to the document index.
        timeout: int
            Timeout for the request (default: 60 seconds)