Module knowledge.services.group
===============================

Classes
-------

`Group(tenant_id: str, group_id: str, owner: str, name: str, join_key: str, rights: knowledge.base.access.GroupAccessRight)`
:   Group
    -----
    In Personal Knowledge backend users can be logically grouped.
    
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
        Access right for group

    ### Descendants

    * knowledge.services.group.GroupInfo

    ### Static methods

    `parse(param: Dict[str, Any]) ‑> knowledge.services.group.Group`
    :

    ### Instance variables

    `group_access_rights: knowledge.base.access.GroupAccessRight`
    :   Rights for group.

    `id: str`
    :   Group id.

    `join_key: str`
    :   Key for joining the group.

    `name: str`
    :   Name of the group.

    `owner_id: Optional[str]`
    :   Owner id (internal id) of the user, who owns the group.

    `tenant_id: str`
    :   Tenant ID.

`GroupInfo(tenant_id: str, group_id: str, owner: str, name: str, join_key: str, rights: knowledge.base.access.GroupAccessRight, group_users: List[knowledge.services.users.User])`
:   Group Information
    -----------------
    Provides additional information on the group.
    Users within the group are listed.

    ### Ancestors (in MRO)

    * knowledge.services.group.Group

    ### Static methods

    `parse(param: Dict[str, Any]) ‑> knowledge.services.group.GroupInfo`
    :

    ### Instance variables

    `group_users: List`
    :   List of all users that are part of the group.

`GroupManagementServiceAPI(service_url: str = 'https://stage-private-knowledge.wacom.com', service_endpoint: str = 'graph')`
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

    `SERVICE_URL: str`
    :

    ### Methods

    `add_entity_to_group(self, auth_key: str, group_id: str, entity_uri: str)`
    :   Adding a entity to group.
        
        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        entity_uri: str
            Entity URI
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `add_user_to_group(self, auth_key: str, group_id: str, user_id: str)`
    :   Adding a user to group.
        
        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        user_id: str
            User who is added to the group
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `create_group(self, auth_key: str, name: str, rights: knowledge.base.access.GroupAccessRight = [Read]) ‑> knowledge.services.group.Group`
    :   Creates a group.
        
        Parameters
        ----------
        auth_key: str
            User key.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        
        Returns
        -------
        group: Group
            Instance of the group.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `delete_group(self, auth_key: str, group_id: str)`
    :   Delete a group.
        
         Parameters
         ----------
         auth_key: str
             User key.
         group_id: str
             ID of the group.
        
         Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `group(self, auth_key: str, group_id: str) ‑> knowledge.services.group.GroupInfo`
    :   Get a group.
        
        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        
        Returns
        -------
        group: Group
            Instance of the group
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `join_group(self, auth_key: str, group_id: str, join_key: str)`
    :   User joining a group with his auth token.
        
        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        join_key: str
            Key which is used to join the group.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `leave_group(self, auth_key: str, group_id: str)`
    :   User leaving a group with his auth token.
        
        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `listing_groups(self, auth_key: str, admin: bool = False) ‑> List[knowledge.services.group.Group]`
    :   Listing all groups configured for this instance.
        
        Parameters
        ----------
        auth_key: str
            API key for authentication
        
        admin: bool (default:= False)
            Uses admin privilege to show all groups of the tenant.
            Requires user to have the role: TenantAdmin
        
        Returns
        -------
        user:  List[Groups]
            List of groups.

    `remove_entity_to_group(self, auth_key: str, group_id: str, entity_uri: str)`
    :   Remove a entity from group.
        
        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        entity_uri: str
            URI of entity
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `remove_user_to_group(self, auth_key: str, group_id: str, user_id: str)`
    :   Remove a user to group.
        
        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        user_id: str
            User who is remove from the group
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `update_group(self, auth_key: str, group_id: str, name: str, rights: knowledge.base.access.GroupAccessRight = knowledge.base.access.GroupAccessRight)`
    :   Updates a group.
        
        Parameters
        ----------
        auth_key: str
            User key.
        group_id: str
            ID of the group.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.