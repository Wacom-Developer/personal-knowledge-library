Module knowledge.services.asyncio.users
=======================================

Classes
-------

`AsyncUserManagementService(application_name: str, service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph/v1')`
:   Async User-Management Service API
    ---------------------------------
    Functionality:
        - List all users
        - Create / update / delete users
    
    Parameters
    ----------
    application_name: str
        Name of the application
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint

    ### Ancestors (in MRO)

    * knowledge.services.asyncio.base.AsyncServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `USER_DETAILS_ENDPOINT: str`
    :

    ### Methods

    `create_user(self, tenant_key: str, external_id: str, meta_data: Dict[str, str] = None, roles: List[knowledge.services.users.UserRole] = None) ‑> Tuple[knowledge.services.users.User, str, str, datetime.datetime]`
    :   Creates user for a tenant.
        
        Parameters
        ----------
        tenant_key: str -
            API key for tenant
        external_id: str -
            External id of user identification service.
        meta_data: Dict[str, str]
            Meta-data dictionary.
        roles: List[UserRole]
            List of roles.
        
        Returns
        -------
        user: User
            Instance of the user
        token: str
            Auth token for user
        refresh_key: str
            Refresh token
        expiration_time: datetime
            Expiration time
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `delete_user(self, tenant_key: str, external_id: str, internal_id: str, force: bool = False)`
    :   Deletes user from tenant.
        
        Parameters
        ----------
        tenant_key: str
            API key for tenant
        external_id: str
            External id of user identification service.
        internal_id: str
            Internal id of user.
        force: bool
            If set to true removes all user data including groups and entities.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `listing_users(self, tenant_key: str, offset: int = 0, limit: int = 20) ‑> List[knowledge.services.users.User]`
    :   Listing all users configured for this instance.
        
        Parameters
        ----------
        tenant_key: str
            API key for tenant
        offset: int - [optional]
            Offset value to define starting position in list. [DEFAULT:= 0]
        limit: int - [optional]
            Define the limit of the list size. [DEFAULT:= 20]
        
        Returns
        -------
        user: List[User]
            List of users.

    `update_user(self, tenant_key: str, internal_id: str, external_id: str, meta_data: Dict[str, str] = None, roles: List[knowledge.services.users.UserRole] = None)`
    :   Updates user for a tenant.
        
        Parameters
        ----------
        tenant_key: str
            API key for tenant
        internal_id: str
            Internal id of semantic service.
        external_id: str
            External id of user identification service.
        meta_data: Dict[str, str]
            Meta-data dictionary.
        roles: List[UserRole]
            List of roles.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `user_internal_id(self, tenant_key: str, external_id: str) ‑> str`
    :   User internal id.
        
        Parameters
        ----------
        tenant_key: str
            API key for tenant
        external_id: str
            External id of user
        
        Returns
        -------
        internal_user_id: str
            Internal id of users
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.