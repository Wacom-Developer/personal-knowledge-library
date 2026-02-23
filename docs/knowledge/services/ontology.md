Module knowledge.services.ontology
==================================

Classes
-------

`OntologyService(service_url: str, application_name: str = 'Ontology Service', base_auth_url: str | None = None, service_endpoint: str = 'ontology/v1', max_retries: int = 3, backoff_factor: float = 0.1)`
:   Ontology API Client
    -------------------
    Client to access the ontology service. Offers the following functionality:
    - Listing class names and property names
    - Create new ontology types
    - Update ontology types
    
    Parameters
    ----------
    application_name: str
        Name of the application.
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    max_retries: int
        Maximum number of retries for failed requests.
    backoff_factor: float
        Backoff factor between retries.
    
    Examples
    --------
    >>> from knowledge.services.ontology import OntologyService
    >>>
    >>> # Initialize the client
    >>> client = OntologyService(
    ...     service_url="https://private-knowledge.wacom.com"
    ... )
    >>> client.login(tenant_api_key="<tenant_key>", external_user_id="<user_id>")
    >>>
    >>> # Get ontology context
    >>> context = client.context()
    >>>
    >>> # List all concepts (classes)
    >>> concepts = client.concepts()
    >>> for concept in concepts:
    ...     print(f"Class: {concept.iri}")
    >>>
    >>> # List all properties
    >>> properties = client.properties()

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `CONCEPTS_ENDPOINT: str`
    :   The type of the None singleton.

    `CONTEXT_ENDPOINT: str`
    :   The type of the None singleton.

    `PROPERTIES_ENDPOINT: str`
    :   The type of the None singleton.

    `PROPERTY_ENDPOINT: str`
    :   The type of the None singleton.

    `RDF_ENDPOINT: str`
    :   The type of the None singleton.

    ### Methods

    `commit(self, context: str, force: bool = False, auth_key: str | None = None, timeout: int = 30) ‑> None`
    :   Commit the ontology.
        
        Parameters
        ----------
        context: str
            Name of the context.
        force: bool (default:= False)
            Force commit of the ontology.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

    `concept(self, context: str, concept_name: str, auth_key: str | None = None, timeout: int = 30) ‑> knowledge.base.ontology.OntologyClass`
    :   Retrieve a concept instance.
        
        **Remark:**
        Works for users with the role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Name of the context
        concept_name: str
            IRI of the concept
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        instance: OntologyClass
            Instance of the concept

    `concepts(self, context: str, auth_key: str | None = None, timeout: int = 30) ‑> List[Tuple[knowledge.base.ontology.OntologyClassReference, knowledge.base.ontology.OntologyClassReference | None]]`
    :   Retrieve all concept classes.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of the ontology
        auth_key: Optional[str] = None
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        concepts: List[Tuple[OntologyClassReference, Optional[OntologyClassReference]]]
            List of ontology classes. Tuple<Classname, Superclass>

    `concepts_types(self, context: str, auth_key: str | None = None, timeout: int = 30) ‑> List[knowledge.base.ontology.OntologyClass]`
    :   Retrieve all concept class types.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of the ontology
        auth_key: Optional[str] = None
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        concepts: List[OntologyClass]
            List of ontology classes.

    `context(self, auth_key: str | None = None, timeout: int = 30) ‑> knowledge.base.ontology.OntologyContext | None`
    :   Getting the information on the context.
        
        Parameters
        ----------
        auth_key: Optional[str] = None
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        context_description: Optional[OntologyContext]
            Context of the Ontology

    `context_metadata(self, context: str, auth_key: str | None = None, timeout: int = 30) ‑> List[knowledge.base.ontology.InflectionSetting]`
    :   Getting the meta-data on the context.
        
        Parameters
        ----------
        context: str
            Name of the context.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        list_inflection_settings: List[InflectionSetting]
            List of inflection settings.

    `create_concept(self, context: str, reference: knowledge.base.ontology.OntologyClassReference, subclass_of: knowledge.base.ontology.OntologyClassReference = wacom:core#Thing, icon: str | None = None, labels: List[knowledge.base.ontology.OntologyLabel] | None = None, comments: List[knowledge.base.ontology.Comment] | None = None, auth_key: str | None = None, timeout: int = 30) ‑> Dict[str, str]`
    :   Create a concept class.
        
        **Remark:**
        Only works for users with the role 'TenantAdmin'.
        
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
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_context(self, name: str, context: str | None = None, base_uri: str | None = None, icon: str | None = None, labels: List[knowledge.base.ontology.OntologyLabel] | None = None, comments: List[knowledge.base.ontology.Comment] | None = None, auth_key: str | None = None, timeout: int = 30) ‑> Dict[str, Any]`
    :   Create context.
        
        **Remark:**
        Only works for users with the role 'TenantAdmin'.
        
        Parameters
        ----------
        base_uri: str
            Base URI
        name: str
            Name of the context.
        context: Optional[str] [default:= None]
            Context of ontology
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the context
        comments: Optional[List[Comment]] (default:= None)
            Comments for the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
                timeout: int
            Timeout for the request (default: 60 seconds)
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        result: Dict[str, Any]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.

    `create_data_property(self, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, domains_cls: List[knowledge.base.ontology.OntologyClassReference], ranges_cls: List[knowledge.base.ontology.DataPropertyType], subproperty_of: knowledge.base.ontology.OntologyPropertyReference | None = None, icon: str | None = None, labels: List[knowledge.base.ontology.OntologyLabel] | None = None, comments: List[knowledge.base.ontology.Comment] | None = None, auth_key: str | None = None, timeout: int = 30) ‑> Dict[str, Any]`
    :   Create a data property.
        
        **Remark:**
        Only works for users with the role 'TenantAdmin'.
        
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
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        result: Dict[str, Any]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.

    `create_object_property(self, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, domains_cls: List[knowledge.base.ontology.OntologyClassReference], ranges_cls: List[knowledge.base.ontology.OntologyClassReference], inverse_of: knowledge.base.ontology.OntologyPropertyReference | None = None, subproperty_of: knowledge.base.ontology.OntologyPropertyReference | None = None, icon: str | None = None, labels: List[knowledge.base.ontology.OntologyLabel] | None = None, comments: List[knowledge.base.ontology.Comment] | None = None, auth_key: str | None = None, timeout: int = 30) ‑> Dict[str, Any]`
    :   Create property.
        
        **Remark:**
        Only works for users with the role 'TenantAdmin'.
        
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
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        
        Returns
        -------
        result: Dict[str, Any]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.

    `delete_concept(self, context: str, reference: knowledge.base.ontology.OntologyClassReference, auth_key: str | None = None, timeout: int = 30) ‑> None`
    :   Delete concept class.
        
        **Remark:**
        Only works for users with the role 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `delete_property(self, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, auth_key: str | None = None, timeout: int = 30) ‑> None`
    :   Delete property.
        
        **Remark:**
        Only works for users with the role 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the property
        auth_key: Optional[str] [default:= None]
            If auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.

    `properties(self, context: str, auth_key: str | None = None, timeout: int = 30) ‑> List[Tuple[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.OntologyPropertyReference | None]]`
    :   List all properties.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Name of the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        contexts: List[Tuple[OntologyPropertyReference, Optional[OntologyPropertyReference]]]
            List of ontology contexts

    `properties_types(self, context: str, auth_key: str | None = None, timeout: int = 30) ‑> List[knowledge.base.ontology.OntologyProperty]`
    :   List all properties types.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        context: str
            Name of the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        contexts: List[OntologyProperty]
            List of ontology contexts

    `property(self, context: str, property_name: str, auth_key: str | None = None, timeout: int = 30) ‑> knowledge.base.ontology.OntologyProperty`
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
            If an auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        instance: OntologyProperty
            Instance of the property

    `rdf_export(self, context: str, version: int = 0, auth_key: str | None = None, timeout: int = 30) ‑> str`
    :   Export RDF.
        
        Parameters
        ----------
        context: str
            Name of the context.
        version: int (default:= 0)
            Version of the context if 0 is set, the latest version will be exported.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        rdf: str
            Ontology as RDFS / OWL ontology

    `remove_context(self, name: str, force: bool = False, auth_key: str | None = None, timeout: int = 30) ‑> None`
    :   Remove context.
        
        Parameters
        ----------
        name: str
            Name of the context
        force: bool (default:= False)
            Force removal of context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Raises
        ------
        WacomServiceException
            Raised if the ontology service returns an error code.

    `update_concept(self, context: str, name: str, subclass_of: str | None, icon: str | None = None, labels: List[knowledge.base.ontology.OntologyLabel] | None = None, comments: List[knowledge.base.ontology.Comment] | None = None, auth_key: str | None = None, timeout: int = 30) ‑> Dict[str, str]`
    :   Update concept class.
        
        **Remark:**
        Only works for users with the role 'TenantAdmin'.
        
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
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        
        Returns
        -------
        response: Dict[str, str]
            Response from service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.