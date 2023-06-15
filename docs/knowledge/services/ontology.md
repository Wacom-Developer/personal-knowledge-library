Module knowledge.services.ontology
==================================

Classes
-------

`OntologyService(service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'ontology/v1')`
:   Ontology API Client
    -------------------
    Client to access the ontology service. Offers the following functionality:
    - Listing class names and property names
    - Create new ontology types
    - Update ontology types
    
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

    `CONCEPTS_ENDPOINT: str`
    :

    `CONTEXT_ENDPOINT: str`
    :

    `PROPERTIES_ENDPOINT: str`
    :

    `PROPERTY_ENDPOINT: str`
    :

    `RDF_ENDPOINT: str`
    :

    ### Methods

    `commit(self, auth_key: str, context: str)`
    :   Commit the ontology.
        
        Parameters
        ----------
        auth_key: str
            User token (must have TenantAdmin) role
        context: str
            Name of the context.

    `concept(self, auth_key: str, context: str, concept_name: str) ‑> knowledge.base.ontology.OntologyClass`
    :   Retrieve a concept instance.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Name of the context
        concept_name: str
            IRI of the concept
        
        Returns
        -------
        instance: OntologyClass
            Instance of the concept

    `concepts(self, auth_key: str, context: str) ‑> list[tuple[knowledge.base.ontology.OntologyClassReference, knowledge.base.ontology.OntologyClassReference]]`
    :   Retrieve all concept classes.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of the ontology
        
        Returns
        -------
        concepts: list[tuple[OntologyClassReference, OntologyClassReference]]
            List of ontology classes. Tuple<Classname, Superclass>

    `context(self, auth_key: str) ‑> Optional[knowledge.base.ontology.OntologyContext]`
    :   Getting the information on the context.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        
        Returns
        -------
        context_description: Optional[OntologyContext]
            Context of the Ontology

    `context_metadata(self, auth_key: str, context: str) ‑> list[knowledge.base.ontology.InflectionSetting]`
    :   Getting the meta-data on the context.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Name of the context.
        
        Returns
        -------
        list_inflection_settings: list[InflectionSetting]
            List of inflection settings.

    `create_concept(self, auth_key: str, context: str, reference: knowledge.base.ontology.OntologyClassReference, subclass_of: knowledge.base.ontology.OntologyClassReference = wacom:core#Thing, icon: Optional[str] = None, labels: Optional[list[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[list[knowledge.base.ontology.Comment]] = None) ‑> dict[str, str]`
    :   Create concept class.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        subclass_of: OntologyClassReference (default:=wacom:core#Thing)
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[list[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[list[Comment]] (default:= None)
            Comments for the class
        Returns
        -------
        result: dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_context(self, auth_key: str, name: str, base_uri: Optional[str] = None, icon: Optional[str] = None, labels: list[knowledge.base.ontology.OntologyLabel] = None, comments: list[knowledge.base.ontology.Comment] = None) ‑> dict[str, str]`
    :   Create context.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        base_uri: str
            Base URI
        name: str
            Name of the context
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[list[OntologyLabel]] (default:= None)
            Labels for the context
        comments: Optional[list[Comment]] (default:= None)
            Comments for the context
        
        Returns
        -------
        result: dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_data_property(self, auth_key: str, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, domains_cls: list[knowledge.base.ontology.OntologyClassReference], ranges_cls: list[knowledge.base.ontology.DataPropertyType], subproperty_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, icon: Optional[str] = None, labels: Optional[list[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[list[knowledge.base.ontology.Comment]] = None) ‑> dict[str, str]`
    :   Create data property.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domains_cls: list[OntologyClassReference]
            IRI of the domain
        ranges_cls: list[DataPropertyType]
            Data property type
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[list[Label]] (default:= None)
            Labels for the class
        comments: Optional[list[Comment]] (default:= None)
            Comments for the class
        
        Returns
        -------
        result: dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_object_property(self, auth_key: str, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, domains_cls: list[knowledge.base.ontology.OntologyClassReference], ranges_cls: list[knowledge.base.ontology.OntologyClassReference], inverse_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, subproperty_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, icon: Optional[str] = None, labels: Optional[list[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[list[knowledge.base.ontology.Comment]] = None) ‑> dict[str, str]`
    :   Create property.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domains_cls: list[OntologyClassReference]
            IRI of the domain
        ranges_cls: list[OntologyClassReference]
            IRI of the range
        inverse_of: Optional[OntologyPropertyReference] (default:= None)
            Inverse property
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[list[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[list[Comment]] (default:= None)
            Comments for the class
        
        Returns
        -------
        result: dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `delete_concept(self, auth_key: str, context: str, reference: knowledge.base.ontology.OntologyClassReference)`
    :   Delete concept class.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `delete_property(self, auth_key: str, context: str, reference: knowledge.base.ontology.OntologyPropertyReference)`
    :   Delete property.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the property
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `properties(self, auth_key: str, context: str) ‑> list[tuple[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.OntologyPropertyReference]]`
    :   List all properties.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Name of the context
        
        Returns
        -------
        contexts: list[tuple[OntologyPropertyReference, OntologyPropertyReference]]
            List of ontology contexts

    `property(self, auth_key: str, context: str, property_name: str) ‑> knowledge.base.ontology.OntologyProperty`
    :   Retrieve a property instance.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Name of the context
        property_name: str
            IRI of the property
        
        Returns
        -------
        instance: OntologyProperty
            Instance of the property

    `rdf_export(self, auth_key: str, context: str) ‑> str`
    :   Export RDF.
        
        Parameters
        ----------
        auth_key: str
            User token (must have TenantAdmin) role
        context: str
            Name of the context.
        
        Returns
        -------
        rdf: str
            Ontology as RDFS / OWL  ontology

    `remove_context(self, auth_key: str, name: str, force: bool = False)`
    :

    `update_concept(self, auth_key: str, context: str, name: str, subclass_of: Optional[str], icon: Optional[str] = None, labels: Optional[list[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[list[knowledge.base.ontology.Comment]] = None) ‑> dict[str, str]`
    :   Update concept class.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context: str
            Context of ontology
        name: str
            Name of the concept
        subclass_of: Optional[str]
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[list[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[list[Comment]] (default:= None)
            Comments for the class
        
        Returns
        -------
        response: dict[str, str]
            Response from service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.