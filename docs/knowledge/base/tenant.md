Module knowledge.base.tenant
============================

Classes
-------

`TenantConfiguration(identifier: str, ontology_name: str, ontology_version: int, is_locked: bool, name: str, rights: List[str], vector_search_data_properties: List[str], vector_search_object_properties: List[str], content_data_property_name: str)`
:   Tenant configuration
    ====================
    
    This class represents the configuration of a tenant.
    The configuration includes the following properties:
        - identifier: str
        - ontology_name: str
        - ontology_version: int
        - is_locked: bool
        - name: str
        - rights: List[str]
    
    Parameters
    ----------
    identifier: str
        Identifier of the tenant
    ontology_name: str
        Name of the ontology
    ontology_version: int
        Version of the ontology
    is_locked: bool
        Flag to indicate if the tenant is locked
    name: str
        Name of the tenant
    rights: List[str]
        List of rights
    vector_search_data_properties: List[str]
        List of vector search data properties which are used for vector search in the metadata
    vector_search_object_properties: List[str]
        List of vector search object properties which are used for vector search in the metadata
    content_data_property_name: str
        Name of the content data property which is used for vector search to index documents

    ### Static methods

    `from_dict(data_dict: Dict[str, Any]) ‑> knowledge.base.tenant.TenantConfiguration`
    :   Create a TenantConfiguration object from a dictionary.
        
        Parameters
        ----------
        data_dict: Dict[str, Any]
            Dictionary containing the tenant configuration data.
        
        Returns
        -------
        TenantConfiguration
            The tenant configuration object.

    ### Instance variables

    `content_data_property_name`
    :   Name of the content data property which is used for vector search to index documents.

    `identifier: str`
    :   Identifier of the tenant
        Returns
        -------
        str
            Identifier of the tenant

    `is_locked: bool`
    :   Flag to indicate if the tenant is locked.

    `name: str`
    :   Name of the tenant.

    `ontology_name: str`
    :   Name of the ontology.
        Returns
        -------
        str
            Name of the ontology.

    `ontology_version: int`
    :   Version of the ontology.

    `rights`
    :   List of rights being assigned to the tenant, and will be added to the user's rights in the token.

    `vector_search_data_properties: List[str]`
    :   List of vector search data properties which are used for vector search in the metadata.

    `vector_search_object_properties`
    :   List of vector search object properties which are used for vector search in the metadata.