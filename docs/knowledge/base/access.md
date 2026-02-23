Module knowledge.base.access
============================

Classes
-------

`AccessRight(read: bool, write: bool, delete: bool)`
:   Access rights for entities within a tenant.
    
    Parameters
    ----------
    read: bool (default: = False)
        Read access for entity within tenant.
    write: bool (default:= False)
        Write access for entity within a tenant.
    delete: bool (default:= False)
        Delete access for entity within tenant.

    ### Descendants

    * knowledge.base.access.GroupAccessRight
    * knowledge.base.access.TenantAccessRight

    ### Class variables

    `DELETE: str`
    :   The type of the None singleton.

    `READ: str`
    :   The type of the None singleton.

    `WRITE: str`
    :   The type of the None singleton.

    ### Instance variables

    `delete: bool`
    :   Delete access for tenant.

    `read: bool`
    :   Read access for tenant.

    `write: bool`
    :   Write access for tenant.

    ### Methods

    `to_list(self) ‑> List[str]`
    :   Converts the access to a list of properties.
        
        Returns
        -------
        access_list: List[str]
            List of rights

`GroupAccessRight(read: bool = False, write: bool = False, delete: bool = False)`
:   GroupAccessRight
    -----------------
    Group rights for entities within a group.
    
    Parameters
    ----------
    read: bool (default:= False)
        Read access for entity within a group.
    write: bool (default:= False)
        Write access for entity within a group.
    delete: bool (default:= False)
        Delete access for entity within a group.

    ### Ancestors (in MRO)

    * knowledge.base.access.AccessRight

    ### Static methods

    `parse(param: List[str]) ‑> knowledge.base.access.GroupAccessRight`
    :   Converts the access to a list of properties.
        
        Parameters
        ----------
        param: List[str]
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
    read: bool (default:= False)
        Read access for entity within tenant.
    write: bool (default:= False)
        Write access for entity within a tenant.
    delete: bool (default:= False)
        Delete access for entity within tenant.

    ### Ancestors (in MRO)

    * knowledge.base.access.AccessRight

    ### Static methods

    `parse(param: List[str]) ‑> knowledge.base.access.TenantAccessRight`
    :   Converts the access to a list of properties.
        
        Parameters
        ----------
        param: List[str]
            List of rights
        
        Returns
        -------
        tenant_rights: TenantAccessRight
            Instantiated rights.