Module knowledge.base.access
============================

Classes
-------

`AccessRight(read: bool = False, write: bool = False, delete: bool = False)`
:   Access rights for entities within a tenant.
    
    Parameters
    ----------
    read: bool (default := False)
        Read access for entity within tenant.
    write: bool (default := False)
        Write access for entity within tenant.
    delete: bool (default := False)
        Delete access for entity within tenant.

    ### Descendants

    * knowledge.base.access.GroupAccessRight
    * knowledge.base.access.TenantAccessRight

    ### Class variables

    `DELETE: str`
    :

    `READ: str`
    :

    `WRITE: str`
    :

    ### Instance variables

    `delete: bool`
    :   Delete access for tenant.

    `read: bool`
    :   Read access for tenant.

    `write: bool`
    :   Write access for tenant.

    ### Methods

    `to_list(self) ‑> list[str]`
    :   Converts the access to list of properties.
        
        Returns
        -------
        access_list: list[str]
            List of rights

`GroupAccessRight(read: bool = False, write: bool = False, delete: bool = False)`
:   GroupAccessRight
    -----------------
    Group rights for entities within a group.
    
    Parameters
    ----------
    read: bool (default := False)
        Read access for entity within group.
    write: bool (default := False)
        Write access for entity within group.
    delete: bool (default := False)
        Delete access for entity within group.

    ### Ancestors (in MRO)

    * knowledge.base.access.AccessRight

    ### Static methods

    `parse(param: list[str]) ‑> knowledge.base.access.GroupAccessRight`
    :   Converts the access to list of properties.
        
        Parameters
        ----------
        param: list[str]
            List of rights
        
        Returns
        -------
        group_rights: GroupAccessRight
            Instantiated rights.

`TenantAccessRight(read: bool = False, write: bool = False, delete: bool = False)`
:   TenantAccessRight
    -----------------
    Access rights for entities within a tenant.
    
    Parameters
    ----------
    read: bool (default := False)
        Read access for entity within tenant.
    write: bool (default := False)
        Write access for entity within tenant.
    delete: bool (default := False)
        Delete access for entity within tenant.

    ### Ancestors (in MRO)

    * knowledge.base.access.AccessRight

    ### Static methods

    `parse(param: list[str]) ‑> knowledge.base.access.TenantAccessRight`
    :   Converts the access to list of properties.
        
        Parameters
        ----------
        param: list[str]
            List of rights
        
        Returns
        -------
        tenant_rights: TenantAccessRight
            Instantiated rights.