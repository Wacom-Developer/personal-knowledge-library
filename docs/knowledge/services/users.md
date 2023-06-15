Module knowledge.services.users
===============================

Classes
-------

`User(tenant_id: str, user_id: str, external_user_id: str, meta_data: dict[str, typing.Any], user_roles: list[knowledge.services.users.UserRole])`
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
    meta_data: dict[str, Any]
        Metadata associated with user.
    user_roles: list[UserRole]
        List of user roles.

    ### Static methods

    `parse(param: dict[str, typing.Any]) ‑> knowledge.services.users.User`
    :   Parse user from dictionary.
        Parameters
        ----------
        param: dict[str, Any]
            Dictionary containing user information.
        
        Returns
        -------
        user: User
            Instance of user.

    ### Instance variables

    `external_user_id: str`
    :   External user id, referencing to external user authentication.

    `id: str`
    :   User id.

    `meta_data: dict[str, typing.Any]`
    :   Meta data for user.

    `tenant_id: str`
    :   Tenant ID.

    `user_roles: list[knowledge.services.users.UserRole]`
    :   List of user roles

`UserManagementServiceAPI(service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph/v1')`
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

    `USER_DETAILS_ENDPOINT: str`
    :

    ### Methods

    `create_user(self, tenant_key: str, external_id: str, meta_data: dict[str, str] = None, roles: list[knowledge.services.users.UserRole] = None) ‑> tuple[knowledge.services.users.User, str, str, datetime.datetime]`
    :   Creates user for a tenant.
        
        Parameters
        ----------
        tenant_key: str -
            API key for tenant
        external_id: str -
            External id of user identification service.
        meta_data: dict[str, str]
            Meta-data dictionary.
        roles: list[UserRole]
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

    `listing_users(self, tenant_key: str, offset: int = 0, limit: int = 20) ‑> list[knowledge.services.users.User]`
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
        user: list[User]
            List of users.

    `update_user(self, tenant_key: str, internal_id: str, external_id: str, meta_data: dict[str, str] = None, roles: list[knowledge.services.users.UserRole] = None)`
    :   Updates user for a tenant.
        
        Parameters
        ----------
        tenant_key: str
            API key for tenant
        internal_id: str
            Internal id of semantic service.
        external_id: str
            External id of user identification service.
        meta_data: dict[str, str]
            Meta-data dictionary.
        roles: list[UserRole]
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