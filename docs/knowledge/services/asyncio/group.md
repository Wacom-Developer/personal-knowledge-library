Module knowledge.services.asyncio.group
=======================================

Classes
-------

`AsyncGroupManagementService(service_url: str, application_name: str = 'Group Management Service', base_auth_url: str | None = None, service_endpoint: str = 'graph/v1', verify_calls: bool = True, timeout: int = 60)`
:   Async Group Management Service API
    ----------------------------------
    The service is managing groups.
    
    Functionality:
        - List all groups
        - Create a group
        - Assign users to group
        - Share entities with a group
    
    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    
    Examples
    --------
    >>> import asyncio
    >>> from knowledge.services.asyncio.group import AsyncGroupManagementService
    >>> from knowledge.base.access import GroupAccessRight
    >>>
    >>> async def main():
    ...     client = AsyncGroupManagementService(
    ...         service_url="https://private-knowledge.wacom.com"
    ...     )
    ...     await client.login(tenant_api_key="<tenant_key>", external_user_id="<user_id>")
    ...
    ...     # Create a group with read access
    ...     group = await client.create_group(
    ...         name="My group",
    ...         rights=GroupAccessRight(read=True, write=False, delete=False)
    ...     )
    ...
    ...     # List all groups
    ...     groups = await client.listing_groups()
    >>>
    >>> asyncio.run(main())

    ### Ancestors (in MRO)

    * knowledge.services.asyncio.base.AsyncServiceAPIClient
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
            Entities URI
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (in seconds). Default: 60 seconds.
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
            Default timeout for the request (in seconds). Default: 60 seconds.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `create_group(self, name: str, rights: knowledge.base.access.GroupAccessRight = [Read], auth_key: str | None = None, timeout: int = 60) ‑> knowledge.services.group.Group`
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
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.
        
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
            Default timeout for the request (in seconds). Default: 60 seconds.
        
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
            Default timeout for the request (in seconds). Default: 60 seconds.
        
        Returns
        -------
        group: GroupInfo
            Instance of the group information.
        
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
            Key, which is used to join the group.
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.
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
            Default timeout for the request (in seconds). Default: 60 seconds.
        
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
            Requires a user to have the role: TenantAdmin
        limit: int (default:= 20)
            Maximum number of groups to return.
        offset: int (default:= 0)
            Offset of the first group to return.
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.
        
        Returns
        -------
        user:  List[Groups]
            List of groups.
        
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `remove_entity_to_group(self, group_id: str, entity_uri: str, auth_key: str | None = None, timeout: int = 60) ‑> None`
    :   Remove an entity from a group.
        
        Parameters
        ----------
        group_id: str
            Group ID
        entity_uri: str
            URI of entity
        auth_key: Optional[str]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (in seconds). Default: 60 seconds.
        
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
            User who is removed from the group
        force: bool
            If true, remove user and entities owned by the user if any
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.

    `update_group(self, group_id: str, name: str, rights: knowledge.base.access.GroupAccessRight, auth_key: str | None = None, timeout: int = 60) ‑> None`
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
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Default timeout for the request (in seconds). Default: 60 seconds.
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.