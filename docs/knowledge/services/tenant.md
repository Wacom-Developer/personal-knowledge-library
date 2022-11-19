Module knowledge.services.tenant
================================

Classes
-------

`TenantManagementServiceAPI(tenant_token: str, service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph')`
:   Tenant Management Service API
    -----------------------------
    
    Functionality:
        - List all tenants
        - Create tenants
        - Create users
    
    Parameters
    ----------
    tenant_token: str
        Tenant Management token
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `SERVICE_URL: str`
    :

    `TENANT_ENDPOINT: str`
    :

    `USER_DETAILS_ENDPOINT: str`
    :

    ### Instance variables

    `tenant_management_token: str`
    :   Tenant Management token.

    ### Methods

    `create_tenant(self, name: str) ‑> Dict[str, str]`
    :   Creates a tenant.
        
        Parameters
        ----------
        name: str -
            Name of the tenant
        
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

    `listing_tenant(self) ‑> List[Dict[str, str]]`
    :   Listing all tenants configured for this instance.
        
        Returns
        -------
        tenants:  List[Dict[str, str]]
            List of tenants:
            >>> [
            >>>     {
            >>>        "id": "<Tenant-ID>",
            >>>        "apiKey": "<Tenant-API-Key>",
            >>>        "name": "<Tenant-Name>"
            >>>     },
            >>>     ...
            >>> ]
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.