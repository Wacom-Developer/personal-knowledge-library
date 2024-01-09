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

    `commit(self, context: str, auth_key: Optional[str] = None)`
    :   Commit the ontology.
        
        Parameters
        ----------
        context: str
            Name of the context.
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.

    `concept(self, context: str, concept_name: str, auth_key: Optional[str] = None) ‑> knowledge.base.ontology.OntologyClass`
    :   Retrieve a concept instance.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Name of the context
        concept_name: str
            IRI of the concept
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        instance: OntologyClass
            Instance of the concept

    `concepts(self, context: str, auth_key: Optional[str] = None) ‑> List[Tuple[knowledge.base.ontology.OntologyClassReference, knowledge.base.ontology.OntologyClassReference]]`
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
        concepts: List[Tuple[OntologyClassReference, OntologyClassReference]]
            List of ontology classes. Tuple<Classname, Superclass>

    `context(self, auth_key: Optional[str] = None) ‑> Optional[knowledge.base.ontology.OntologyContext]`
    :   Getting the information on the context.
        
        Parameters
        ----------
        auth_key: Optional[str] [default:= None]
            Auth
        
        Returns
        -------
        context_description: Optional[OntologyContext]
            Context of the Ontology

    `context_metadata(self, context: str, auth_key: Optional[str] = None) ‑> List[knowledge.base.ontology.InflectionSetting]`
    :   Getting the meta-data on the context.
        
        Parameters
        ----------
        context: str
            Name of the context.
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        list_inflection_settings: List[InflectionSetting]
            List of inflection settings.

    `create_concept(self, context: str, reference: knowledge.base.ontology.OntologyClassReference, subclass_of: knowledge.base.ontology.OntologyClassReference = wacom:core#Thing, icon: Optional[str] = None, labels: Optional[List[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[List[knowledge.base.ontology.Comment]] = None, auth_key: Optional[str] = None) ‑> Dict[str, str]`
    :   Create concept class.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        subclass_of: OntologyClassReference (default:=wacom:core#Thing)
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_context(self, name: str, context: Optional[str] = None, base_uri: Optional[str] = None, icon: Optional[str] = None, labels: List[knowledge.base.ontology.OntologyLabel] = None, comments: List[knowledge.base.ontology.Comment] = None, auth_key: Optional[str] = None) ‑> Dict[str, str]`
    :   Create context.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        base_uri: str
            Base URI
        name: str
            Name of the context
        context: Optional[str] [default:= None]
            Context of ontology
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the context
        comments: Optional[List[Comment]] (default:= None)
            Comments for the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_data_property(self, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, domains_cls: List[knowledge.base.ontology.OntologyClassReference], ranges_cls: List[knowledge.base.ontology.DataPropertyType], subproperty_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, icon: Optional[str] = None, labels: Optional[List[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[List[knowledge.base.ontology.Comment]] = None, auth_key: Optional[str] = None) ‑> Dict[str, str]`
    :   Create data property.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domains_cls: List[OntologyClassReference]
            IRI of the domain
        ranges_cls: List[DataPropertyType]
            Data property type
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_object_property(self, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, domains_cls: List[knowledge.base.ontology.OntologyClassReference], ranges_cls: List[knowledge.base.ontology.OntologyClassReference], inverse_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, subproperty_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, icon: Optional[str] = None, labels: Optional[List[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[List[knowledge.base.ontology.Comment]] = None, auth_key: Optional[str] = None) ‑> Dict[str, str]`
    :   Create property.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domains_cls: List[OntologyClassReference]
            IRI of the domain
        ranges_cls: List[OntologyClassReference]
            IRI of the range
        inverse_of: Optional[OntologyPropertyReference] (default:= None)
            Inverse property
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `delete_concept(self, context: str, reference: knowledge.base.ontology.OntologyClassReference, auth_key: Optional[str] = None)`
    :   Delete concept class.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `delete_property(self, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, auth_key: Optional[str] = None)`
    :   Delete property.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the property
        auth_key: Optional[str] [default:= None]
            If auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `properties(self, context: str, auth_key: Optional[str] = None) ‑> List[Tuple[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.OntologyPropertyReference]]`
    :   List all properties.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Name of the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        contexts: List[Tuple[OntologyPropertyReference, OntologyPropertyReference]]
            List of ontology contexts

    `property(self, context: str, property_name: str, auth_key: Optional[str] = None) ‑> knowledge.base.ontology.OntologyProperty`
    :   Retrieve a property instance.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Name of the context
        property_name: str
            IRI of the property
        auth_key: Optional[str] [default:= None]
            If auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        instance: OntologyProperty
            Instance of the property

    `rdf_export(self, context: str, auth_key: Optional[str] = None) ‑> str`
    :   Export RDF.
        
        Parameters
        ----------
        context: str
            Name of the context.
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        rdf: str
            Ontology as RDFS / OWL  ontology

    `remove_context(self, name: str, force: bool = False, auth_key: Optional[str] = None)`
    :   Remove context.
        
        Parameters
        ----------
        name: str
            Name of the context
        force: bool (default:= False)
            Force removal of context
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        Returns
        -------
        result: Dict[str, str]
            Result from the service

    `update_concept(self, context: str, name: str, subclass_of: Optional[str], icon: Optional[str] = None, labels: Optional[List[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[List[knowledge.base.ontology.Comment]] = None, auth_key: Optional[str] = None) ‑> Dict[str, str]`
    :   Update concept class.
        
        **Remark:**
        Only works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of ontology
        name: str
            Name of the concept
        subclass_of: Optional[str]
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        response: Dict[str, str]
            Response from service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.