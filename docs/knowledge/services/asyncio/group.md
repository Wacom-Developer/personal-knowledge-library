Module knowledge.services.asyncio.group
=======================================

Classes
-------

`AsyncGroupManagementService(application_name: str, service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph/v1')`
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

    * knowledge.services.asyncio.base.AsyncServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `GROUP_ENDPOINT: str`
    :   "Endpoint for all group related functionality.

    ### Methods

    `add_entity_to_group(self, group_id: str, entity_uri: str, auth_key: Optional[str] = None)`
    :   Adding an entity to group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            Entity URI
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `add_user_to_group(self, group_id: str, user_id: str, auth_key: Optional[str] = None)`
    :   Adding a user to group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        user_id: str
            User who is added to the group
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `create_group(self, name: str, rights: knowledge.base.access.GroupAccessRight = [Read], auth_key: Optional[str] = None) ‑> knowledge.services.group.Group`
    :   Creates a group.
        
        Parameters
        ----------
        auth_key: str
            User key.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        group: Group
            Instance of the group.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `delete_group(self, group_id: str, force: bool = False, auth_key: Optional[str] = None)`
    :   Delete a group.
        
         Parameters
         ----------
         group_id: str
             ID of the group.
         force: bool (Default = False)
            If True, the group will be deleted even if it is not empty.
         auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `group(self, group_id: str, auth_key: Optional[str] = None) ‑> knowledge.services.group.GroupInfo`
    :   Get a group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        group: GroupInfo
            Instance of the group information.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `join_group(self, group_id: str, join_key: str, auth_key: Optional[str] = None)`
    :   User joining a group with his auth token.
        
        Parameters
        ----------
        group_id: str
            Group ID
        join_key: str
            Key which is used to join the group.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `leave_group(self, group_id: str, auth_key: Optional[str] = None)`
    :   User leaving a group with his auth token.
        
        Parameters
        ----------
        group_id: str
            Group ID
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `listing_groups(self, admin: bool = False, limit: int = 20, offset: int = 0, auth_key: Optional[str] = None) ‑> List[knowledge.services.group.Group]`
    :   Listing all groups configured for this instance.
        
        Parameters
        ----------
        admin: bool (default:= False)
            Uses admin privilege to show all groups of the tenant.
            Requires user to have the role: TenantAdmin
        limit: int (default:= 20)
            Maximum number of groups to return.
        offset: int (default:= 0)
            Offset of the first group to return.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        user:  List[Groups]
            List of groups.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `remove_entity_to_group(self, group_id: str, entity_uri: str, auth_key: Optional[str] = None)`
    :   Remove an entity from group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            URI of entity
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `remove_user_from_group(self, group_id: str, user_id: str, force: bool = False, auth_key: Optional[str] = None)`
    :   Remove a user from group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        user_id: str
            User who is remove from the group
        force: bool
            If true remove user and entities owned by the user if any
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `update_group(self, group_id: str, name: str, rights: knowledge.base.access.GroupAccessRight = knowledge.base.access.GroupAccessRight, auth_key: Optional[str] = None)`
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
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.