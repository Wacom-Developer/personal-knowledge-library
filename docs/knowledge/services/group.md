Module knowledge.services.group
===============================

Classes
-------

`Group(tenant_id: str, group_id: str, owner: str, name: str, join_key: str, rights: knowledge.base.access.GroupAccessRight)`
:   Entities and users can be assigned to groups.
    If the entity is assigned to a group the users have access to the entity with the rights defined in the group.
    
    Parameters
    ----------
    tenant_id: str
        Tenant id
    group_id: str
        Group id
    owner: str
        User id who has created the group.
    name: str
        Name of the group.
    join_key: str
        Key which is required to join the group
    rights: GroupAccessRight
        Access right for group.
    
    Attributes
    ----------
    id: str
        Group identifier
    tenant_id: str
        Tenant identifier
    owner_id: str
        Owner identifier
    name: str
        Name of the group
    join_key: str
        Key which is required to join the group
    group_access_rights: GroupAccessRight
        Access rights for the group

    ### Descendants

    * knowledge.services.group.GroupInfo

    ### Static methods

    `parse(param: Dict[str, Any]) ‑> knowledge.services.group.Group`
    :   Parse group from dictionary.
        
        Arguments
        ---------
        param: Dict[str, Any]
            Dictionary containing group information.
        
        Returns
        -------
        instance: Group
            The group object

    ### Instance variables

    `group_access_rights: knowledge.base.access.GroupAccessRight`
    :   Rights for group.

    `id: str`
    :   Group id.

    `join_key: str`
    :   Key for joining the group.

    `name: str`
    :   Name of the group.

    `owner_id: str | None`
    :   Owner id (internal id) of the user, who owns the group.

    `tenant_id: str`
    :   Tenant ID.

`GroupInfo(tenant_id: str, group_id: str, owner: str, name: str, join_key: str, rights: knowledge.base.access.GroupAccessRight, group_users: List[knowledge.services.users.User])`
:   Extended group information including the list of users in the group.
    
    Parameters
    ----------
    tenant_id : str
        Identifier of the tenant the group belongs to.
    group_id : str
        Unique identifier of the group.
    owner : str
        Owner id of the group.
    name : str
        Display name of the group.
    join_key : str
        Key required to join the group.
    rights : GroupAccessRight
        Access rights associated with the group.
    group_users : List[User]
        Users that belong to the group.
    
    Attributes
    ----------
    group_users : List[User]
        List of all users that are part of the group.

    ### Ancestors (in MRO)

    * knowledge.services.group.Group

    ### Instance variables

    `group_users: List[knowledge.services.users.User]`
    :   List of all users that are part of the group.

`GroupManagementService(service_url: str, application_name: str = 'Group Management Service', service_endpoint: str = 'graph/v1')`
:   Group Management Service API
    -----------------------------
    The service is managing groups.
    
    Functionality:
        - List all groups
        - Create group
        - Assign users to group
        - Share entities with group
    
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

    `GROUP_ENDPOINT: str`
    :   "Endpoint for all group related functionality.

    ### Methods

    `add_entity_to_group(self, group_id: str, entity_uri: str, auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   Adding an entity to a group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            Entity URI
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `add_user_to_group(self, group_id: str, user_id: str, auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   Adding a user to a group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        user_id: str
            User who is added to the group
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `create_group(self, name: str, rights: knowledge.base.access.GroupAccessRight = [Read], auth_key: str | None = None, timeout: int = 60) ‑> knowledge.services.group.Group`
    :   Creates a group.
        
        Parameters
        ----------
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        group: Group
            Instance of the group.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `delete_group(self, group_id: str, force: bool = False, auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   Delete a group.
        
        Parameters
        ----------
        group_id: str
            ID of the group.
        force: bool (Default = False)
            If True, the group will be deleted even if it is not empty.
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Raises
        ------
        WacomServiceException
        If the tenant service returns an error code.

    `group(self, group_id: str, auth_key: str | None = None, timeout: int = 60) ‑> knowledge.services.group.GroupInfo`
    :   Get a group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        group: GroupInfo
            Instance of the group
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `join_group(self, group_id: str, join_key: str, auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   User joining a group with his auth token.
        
        Parameters
        ----------
        group_id: str
            Group ID
        join_key: str
            Key which is used to join the group.
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `leave_group(self, group_id: str, auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   User leaving a group with his auth token.
        
        Parameters
        ----------
        group_id: str
            Group ID
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `listing_groups(self, admin: bool = False, limit: int = 20, offset: int = 0, auth_key: str | None = None, timeout: int = 60) ‑> List[knowledge.services.group.Group]`
    :   Listing all groups configured for this instance.
        
        Parameters
        ----------
        admin: bool (default:= False)
            Uses admin privilege to show all groups of the tenants.
            Requires user to have the role: TenantAdmin
        limit: int (default:= 20)
            Maximum number of groups to return.
        offset: int (default:= 0)
            Offset of the first group to return.
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        user:  List[Groups]
            List of groups.

    `remove_entity_to_group(self, group_id: str, entity_uri: str, auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   Remove an entity from group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            URI of entity
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `remove_user_from_group(self, group_id: str, user_id: str, force: bool = False, auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   Remove a user from a group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        user_id: str
            User who is remove from the group
        force: bool
            If true remove user and entities owned by the user if any
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `update_group(self, group_id: str, name: str, rights: knowledge.base.access.GroupAccessRight = [Read], auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   Updates a group.
        
        Parameters
        ----------
        group_id: str
            ID of the group.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.