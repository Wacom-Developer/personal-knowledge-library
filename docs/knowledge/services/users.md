Module knowledge.services.users
===============================

Classes
-------

`User(tenant_id: str, user_id: str, external_user_id: str, meta_data: Dict[str, Any], user_roles: List[knowledge.services.users.UserRole])`
:   User
    -----
    In Personal Knowledge backend is linking a user to a shadow user which is used within the personal knowledge graph.
    
    Parameters
    ----------
    tenant_id: str
        Tenant id
    user_id: str
        User id
    external_user_id: str
        External user id, referencing the user to authentication system.
    meta_data: Dict[str, Any]
        Metadata associated with user.
    user_roles: List[UserRole]
        List of user roles.

    ### Static methods

    `parse(param: Dict[str, Any]) ‑> knowledge.services.users.User`
    :

    ### Instance variables

    `external_user_id: str`
    :   External user id, referencing to external user authentication.

    `id: str`
    :   User id.

    `meta_data: Dict[str, Any]`
    :   Meta data for user.

    `tenant_id: str`
    :   Tenant ID.

    `user_roles: List[knowledge.services.users.UserRole]`
    :   List of user roles

`UserManagementServiceAPI(service_url: str = 'https://stage-private-knowledge.wacom.com', service_endpoint: str = 'graph')`
:   User-Management Service API
    -----------------------------
    
    Functionality:
        - List all users
        - Create / update / delete users
    
    Parameters
    ----------
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

    `USER_DETAILS_ENDPOINT: str`
    :

    ### Methods

    `create_user(self, tenant_key: str, external_id: str, meta_data: Dict[str, str] = None, roles: List[knowledge.services.users.UserRole] = None) ‑> Tuple[knowledge.services.users.User, str]`
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
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `delete_user(self, tenant_key: str, external_id: str, internal_id: str)`
    :   Deletes user from tenant.
        
        Parameters
        ----------
        tenant_key: str
            API key for tenant
        external_id: str
            External id of user identification service.
        internal_id: str
            Internal id of user.
        
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

`UserRole(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   UserRole
    --------
    Roles of the users in

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ADMIN`
    :   TenantAdmin has access to all entities independent of the access rights.

    `USER`
    :   User only has control over his personal entities.