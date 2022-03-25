Module knowledge.services.ontology
==================================

Classes
-------

`OntologyService(service_url: str, service_endpoint: str = 'ontology')`
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

    `COMMIT_ENDPOINT: str`
    :

    `CONCEPTS_ENDPOINT: str`
    :

    `CONCEPT_ENDPOINT: str`
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

    `commit(self, auth_key: str, context_name: str)`
    :   Commit the ontology.
        
        Parameters
        ----------
        auth_key: str
            User token (must have TenantAdmin) role
        context_name: str
            Name of the context.

    `concept(self, auth_key: str, context_name: str, concept_name: str) ‑> knowledge.base.ontology.OntologyClass`
    :   Retrieve a concept instance.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context_name: str
            Name of the context
        concept_name: str
            IRI of the concept
        
        Returns
        -------
        instance: OntologyClass
            Instance of the concept

    `concepts(self, auth_key: str, context: str) ‑> List[Tuple[knowledge.base.ontology.OntologyClassReference, knowledge.base.ontology.OntologyClassReference]]`
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

    `contexts(self, auth_key: str) ‑> List[knowledge.base.entity.OntologyContext]`
    :   List all concepts.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        
        Returns
        -------
        contexts: List[OntologyContext]
            List of ontology contexts

    `create_concept(self, auth_key: str, context: str, reference: knowledge.base.ontology.OntologyClassReference, subclass_of: knowledge.base.ontology.OntologyClassReference = wacom:core#Thing, icon: Optional[str] = None, labels: Optional[List[knowledge.base.entity.Label]] = None, comments: Optional[List[knowledge.base.entity.Comment]] = None) ‑> Dict[str, str]`
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
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_context(self, auth_key: str, name: str, base_uri: Optional[str] = None, icon: Optional[str] = None, labels: List[knowledge.base.entity.Label] = None, comments: List[knowledge.base.entity.Comment] = None) ‑> Dict[str, str]`
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
        labels: Optional[List[Label]] (default:= None)
            Labels for the context
        comments: Optional[List[Comment]] (default:= None)
            Comments for the context
        
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_data_property(self, auth_key: str, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, domain_cls: knowledge.base.ontology.OntologyClassReference, range_cls: knowledge.base.ontology.DataPropertyType, subproperty_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, icon: Optional[str] = None, labels: Optional[List[knowledge.base.entity.LocalizedContent]] = None, comments: Optional[List[knowledge.base.entity.LocalizedContent]] = None) ‑> Dict[str, str]`
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
        domain_cls: OntologyClassReference
            IRI of the domain
        range_cls: DataPropertyType
            Data property type
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `create_object_property(self, auth_key: str, context: str, reference: knowledge.base.ontology.OntologyPropertyReference, domain_cls: knowledge.base.ontology.OntologyClassReference, range_cls: knowledge.base.ontology.OntologyClassReference, inverse_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, subproperty_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, icon: Optional[str] = None, labels: Optional[List[knowledge.base.entity.LocalizedContent]] = None, comments: Optional[List[knowledge.base.entity.LocalizedContent]] = None) ‑> Dict[str, str]`
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
        domain_cls: OntologyClassReference
            IRI of the domain
        range_cls: OntologyClassReference
            IRI of the range
        inverse_of: Optional[OntologyPropertyReference] (default:= None)
            Inverse property
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        
        Returns
        -------
        result: Dict[str, str]
            Result from the service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.

    `properties(self, auth_key: str, context_name: str) ‑> List[Tuple[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.OntologyPropertyReference]]`
    :   List all properties.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context_name: str
            Name of the context
        
        Returns
        -------
        contexts: List[Tuple[OntologyPropertyReference, OntologyPropertyReference]]
            List of ontology contexts

    `property(self, auth_key: str, context_name: str, property_name: str) ‑> knowledge.base.ontology.OntologyProperty`
    :   Retrieve a property instance.
        
        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user.
        context_name: str
            Name of the context
        property_name: str
            IRI of the property
        
        Returns
        -------
        instance: OntologyProperty
            Instance of the property

    `rdf_export(self, auth_key: str, context_name: str) ‑> str`
    :   Export RDF.
        
        Parameters
        ----------
        auth_key: str
            User token (must have TenantAdmin) role
        context_name: str
            Name of the context.
        
        Returns
        -------
        rdf: str
            Ontology as RDFS / OWL  ontology

    `update_concept(self, auth_key: str, context: str, name: str, subclass_of: Optional[str], icon: Optional[str] = None, labels: Optional[List[knowledge.base.entity.Label]] = None, comments: Optional[List[knowledge.base.entity.Comment]] = None) ‑> Dict[str, str]`
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
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        
        Returns
        -------
        response: Dict[str, str]
            Response from service
        
        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.