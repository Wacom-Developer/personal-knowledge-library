Module knowledge.services.asyncio.graph
=======================================

Classes
-------

`AsyncWacomKnowledgeService(application_name: str, service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph/v1', graceful_shutdown: bool = False)`
:   AsyncWacomKnowledgeService
    ---------------------
    Client for the Semantic Ink Private knowledge system.
    
    Operations for entities:
        - Creation of entities
        - Update of entities
        - Deletion of entities
        - Listing of entities
    
    Parameters
    ----------
    application_name: str
        Name of the application
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint

    ### Ancestors (in MRO)

    * knowledge.services.asyncio.base.AsyncServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `ACTIVATIONS_ENDPOINT: str`
    :

    `ENTITY_BULK_ENDPOINT: str`
    :

    `ENTITY_ENDPOINT: str`
    :

    `ENTITY_IMAGE_ENDPOINT: str`
    :

    `LISTING_ENDPOINT: str`
    :

    `NAMED_ENTITY_LINKING_ENDPOINT: str`
    :

    `ONTOLOGY_UPDATE_ENDPOINT: str`
    :

    `RELATIONS_ENDPOINT: str`
    :

    `RELATION_ENDPOINT: str`
    :

    `SEARCH_DESCRIPTION_ENDPOINT: str`
    :

    `SEARCH_LABELS_ENDPOINT: str`
    :

    `SEARCH_LITERALS_ENDPOINT: str`
    :

    `SEARCH_RELATION_ENDPOINT: str`
    :

    `SEARCH_TYPES_ENDPOINT: str`
    :

    `USER_ENDPOINT: str`
    :

    ### Methods

    `activations(self, uris: List[str], depth: int, auth_key: str | None = None) ‑> Tuple[Dict[str, knowledge.base.ontology.ThingObject], List[Tuple[str, knowledge.base.ontology.OntologyPropertyReference, str]]]`
    :   Spreading activation, retrieving the entities related to an entity.
        
        Parameters
        ----------
        uris: List[str]
            List of URIS for entity.
        depth: int
            Depth of activations
        auth_key: Optional[str] [default:=None]
            Use a different auth key than the one from the client
        
        Returns
        -------
        entity_map: Dict[str, ThingObject]
            Map with entity and its URI as key.
        relations: List[Tuple[str, OntologyPropertyReference, str]]
            List of relations with subject predicate, (Property), and subject
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code, and activation failed.

    `create_entity(self, entity: knowledge.base.ontology.ThingObject, auth_key: str | None = None, ignore_image: bool = False) ‑> str`
    :   Creates entity in graph.
        
        Parameters
        ----------
        entity: ThingObject
            Entities object that needs to be created
        auth_key: Optional[str]
            Use a different auth key than the one from the client
        ignore_image: bool
            Ignore image.
        
        Returns
        -------
        uri: str
            URI of entity
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `create_entity_bulk(self, entities: List[knowledge.base.ontology.ThingObject], batch_size: int = 10, ignore_images: bool = False, auth_key: str | None = None) ‑> List[knowledge.base.ontology.ThingObject]`
    :   Creates entity in graph.
        
        Parameters
        ----------
        entities: List[ThingObject]
            Entities
        batch_size: int
            Batch size
        ignore_images: bool
            Do not automatically upload images
        auth_key: Optional[str]
            If auth key is not set, the client auth key will be used.
        
        Returns
        -------
        uris: List[ThingObject]
            List of ThingObjects with URI
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `create_relation(self, source: str, relation: knowledge.base.ontology.OntologyPropertyReference, target: str, auth_key: str | None = None)`
    :   Creates a relation for an entity to a source entity.
        
        Parameters
        ----------
        source: str
            Entities URI of the source
        relation: OntologyPropertyReference
            ObjectProperty property
        target: str
            Entities URI of the target
        auth_key: Optional[str] [default:=None]
            Use a different auth key than the one from the client
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `create_relations_bulk(self, source: str, relations: Dict[knowledge.base.ontology.OntologyPropertyReference, List[str]], auth_key: str | None = None)`
    :   Creates all the relations for an entity to a source entity.
        
        Parameters
        ----------
        source: str
            Entities URI of the source
        
        relations: Dict[OntologyPropertyReference, List[str]]
            ObjectProperty property and targets mapping.
        
        auth_key: Optional[str] = None
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `delete_entities(self, uris: List[str], force: bool = False, auth_key: str | None = None)`
    :   Delete a list of entities.
        
        Parameters
        ----------
        uris: List[str]
            List of URI of entities. **Remark:** More than 100 entities are not possible in one request
        force: bool
            Force deletion process
        auth_key: Optional[str]
            Use a different auth key than the one from the client
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code
        ValueError
            If more than 100 entities are given

    `delete_entity(self, uri: str, force: bool = False, auth_key: str | None = None)`
    :   Deletes an entity.
        
        Parameters
        ----------
        uri: str
            URI of entity
        force: bool
            Force deletion process
        auth_key: Optional[str]
            Use a different auth key than the one from the client
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `entity(self, uri: str, auth_key: str | None = None) ‑> knowledge.base.ontology.ThingObject`
    :   Retrieve entity information from personal knowledge, using the  URI as identifier.
        
        **Remark:** Object properties (relations) must be requested separately.
        
        Parameters
        ----------
        uri: str
            URI of entity
        auth_key: Optional[str]
            Use a different auth key than the one from the client
        
        Returns
        -------
        thing: ThingObject
            Entities with is type URI, description, an image/icon, and tags (labels).
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code or the entity is not found in the knowledge graph

    `exists(self, uri: str) ‑> bool`
    :   Check if entity exists in knowledge graph.
        
        Parameters
        ----------
        uri: str -
            URI for entity
        
        Returns
        -------
        flag: bool
            Flag if entity does exist

    `labels(self, uri: str, locale: knowledge.base.language.LocaleCode = 'en_US', auth_key: str | None = None) ‑> List[knowledge.base.entity.Label]`
    :   Extract list labels of entity.
        
        Parameters
        ----------
        uri: str
            Entities URI of the source
        locale: str
            ISO-3166 Country Codes and ISO-639 Language Codes in the format <language_code>_<country>, e.g., en_US.
        auth_key: Optional[str] = None
            Use a different auth key than the one from the client
        
        Returns
        -------
        labels: List[Label]
            List of labels of an entity.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `link_personal_entities(self, text: str, language_code: knowledge.base.language.LocaleCode = 'en_US', auth_key: str | None = None) ‑> List[knowledge.nel.base.KnowledgeGraphEntity]`
    :   Performs Named Entities Linking on a text. It only finds entities which are accessible by the user identified by
        the auth key.
        
        Parameters
        ----------
        auth_key: str
            Auth key identifying a user within the Wacom personal knowledge service.
        text: str
            Text where the entities shall be tagged in.
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        
        Returns
        -------
        entities: List[KnowledgeGraphEntity]
            List of knowledge graph entities.
        
        Raises
        ------
        WacomServiceException
            If the Named Entities Linking service returns an error code.

    `listing(self, filter_type: knowledge.base.ontology.OntologyClassReference, page_id: str | None = None, limit: int = 30, locale: knowledge.base.language.LocaleCode | None = None, visibility: knowledge.services.graph.Visibility | None = None, is_owner: bool | None = None, estimate_count: bool = False, auth_key: str | None = None) ‑> Tuple[List[knowledge.base.ontology.ThingObject], int, str]`
    :   List all entities visible to users.
        
        Parameters
        ----------
        filter_type: OntologyClassReference
            Filtering with entity
        page_id: Optional[str]
            Page id. Start from this page id
        limit: int
            Limit of the returned entities.
        locale: Optional[LocaleCode] [default:=None]
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        visibility: Optional[Visibility] [default:=None]
            Filter the entities based on its visibilities
        is_owner: Optional[bool] [default:=None]
            Filter the entities based on its owner
        estimate_count: bool [default:=False]
            Request an estimate of the entities in a tenant.
        auth_key: Optional[str]
            Auth key from user if not set, the client auth key will be used
        
        Returns
        -------
        entities: List[ThingObject]
            List of entities
        estimated_total_number: int
            Number of all entities
        next_page_id: str
            Identifier of the next page
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `literals(self, uri: str, locale: knowledge.base.language.LocaleCode = 'en_US', auth_key: str | None = None) ‑> List[knowledge.base.ontology.DataProperty]`
    :   Collect all literals of entity.
        
        Parameters
        ----------
        uri: str
            Entities URI of the source
        locale: LocaleCode [default:=EN_US]
            ISO-3166 Country Codes and ISO-639 Language Codes in the format <language_code>_<country>, e.g., en_US.
        auth_key: Optional[str] [default:=None]
            Use a different auth key than the one from the client
        Returns
        -------
        literals: List[DataProperty]
            List of data properties of an entity.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `ontology_update(self, fix: bool = False, auth_key: str | None = None)`
    :   Update the ontology.
        
        **Remark:**
        Works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        fix: bool [default:=False]
            Fix the ontology if tenant is in inconsistent state.
        auth_key: Optional[str] [default:=None]
            Auth key from user if not set, the client auth key will be used
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code and commit failed.

    `relations(self, uri: str, auth_key: str | None = None) ‑> Dict[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.ObjectProperty]`
    :   Retrieve the relations (object properties) of an entity.
        
        Parameters
        ----------
        uri: str
            Entities URI of the source
        
        auth_key: Optional[str]
            Use a different auth key than the one from the client
        
        Returns
        -------
        relations: Dict[OntologyPropertyReference, ObjectProperty]
            All relations a dict
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `remove_relation(self, source: str, relation: knowledge.base.ontology.OntologyPropertyReference, target: str, auth_key: str | None = None)`
    :   Removes a relation.
        
        Parameters
        ----------
        source: str
            Entities uri of the source
        relation: OntologyPropertyReference
            ObjectProperty property
        target: str
            Entities uri of the target
        auth_key: Optional[str] [default:=None]
            Use a different auth key than the one from the client
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `search_all(self, search_term: str, language_code: knowledge.base.language.LocaleCode, types: List[knowledge.base.ontology.OntologyClassReference], limit: int = 30, next_page_id: str = None, auth_key: str | None = None) ‑> Tuple[List[knowledge.base.ontology.ThingObject], str]`
    :   Search term in labels, literals and description.
        
        Parameters
        ----------
        search_term: str
            Search term.
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        types: List[OntologyClassReference]
            Limits the types for search.
        limit: int  (default:= 30)
            Size of the page for pagination.
        next_page_id: str [default:=None]
            ID of the next page within pagination.
        auth_key: Optional[str] [default:=None]
            Auth key from user if not set, the client auth key will be used
        
        Returns
        -------
        results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `search_description(self, search_term: str, language_code: knowledge.base.language.LocaleCode, limit: int = 30, auth_key: str | None = None, next_page_id: str = None) ‑> Tuple[List[knowledge.base.ontology.ThingObject], str]`
    :   Search for matches in description.
        
        Parameters
        ----------
        search_term: str
            Search term.
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        limit: int  (default:= 30)
            Size of the page for pagination.
        auth_key: Optional[str] [default:=None]
            Auth key from user if not set, the client auth key will be used
        next_page_id: str [default:=None]
            ID of the next page within pagination.
        
        Returns
        -------
        results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `search_labels(self, search_term: str, language_code: knowledge.base.language.LocaleCode, exact_match: bool = False, limit: int = 30, next_page_id: str = None, auth_key: str | None = None) ‑> Tuple[List[knowledge.base.ontology.ThingObject], str]`
    :   Search for matches in labels.
        
        Parameters
        ----------
        search_term: str
            Search term.
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        exact_match: bool [default:=False]
            Exact match of the search term.
        limit: int  (default:= 30)
            Size of the page for pagination.
        next_page_id: str [default:=None]
            ID of the next page within pagination.
        auth_key: Optional[str] [default:=None]
            Auth key from user if not set, the client auth key will be used
        
        Returns
        -------
        results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `search_literal(self, search_term: str, literal: knowledge.base.ontology.OntologyPropertyReference, pattern: knowledge.services.graph.SearchPattern = SearchPattern.REGEX, language_code: knowledge.base.language.LocaleCode = 'en_US', limit: int = 30, next_page_id: str = None, auth_key: str | None = None) ‑> Tuple[List[knowledge.base.ontology.ThingObject], str]`
    :   Search for matches in literals.
        
         Parameters
         ----------
         search_term: str
             Search term.
         literal: OntologyPropertyReference
             Literal used for the search
         pattern: SearchPattern (default:= SearchPattern.REGEX)
             Search pattern. The chosen search pattern must fit the type of the entity.
         language_code: LocaleCode
             ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
         limit: int (default:= 30)
             Size of the page for pagination.
         next_page_id: str [default:=None]
             ID of the next page within pagination.
         auth_key: Optional[str] [default:=None]
             Auth key from user if not set, the client auth key will be used
         Returns
         -------
         results: List[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `search_relation(self, relation: knowledge.base.ontology.OntologyPropertyReference, language_code: knowledge.base.language.LocaleCode, subject_uri: str = None, object_uri: str = None, limit: int = 30, next_page_id: str = None, auth_key: str | None = None) ‑> Tuple[List[knowledge.base.ontology.ThingObject], str]`
    :   Search for matches in literals.
        
         Parameters
         ----------
         relation: OntologyPropertyReference
             Search term.
         language_code: LocaleCode
             ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
         subject_uri: str [default:=None]
             URI of the subject
         object_uri: str [default:=None]
             URI of the object
         limit: int (default:= 30)
             Size of the page for pagination.
         next_page_id: str [default:=None]
             ID of the next page within pagination.
         auth_key: Optional[str] [default:=None]
             Auth key from user if not set, the client auth key will be used
        
         Returns
         -------
         results: List[ThingObject]
            List of things matching the search term
         next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `set_entity_image(self, entity_uri: str, image_byte: bytes, file_name: str = 'icon.jpg', mime_type: str = 'image/jpeg', auth_key: str | None = None) ‑> str`
    :   Setting the image of the entity.
        The image for the URL is downloaded and then pushed to the backend.
        
        Parameters
        ----------
        entity_uri: str
            URI of the entity.
        image_byte: bytes
            Binary encoded image.
        file_name: str [default:=None]
            Name of  the file. If None the name is extracted from URL.
        mime_type: str [default:=None]
            Mime type.
        auth_key: Optional[str] [default:=None]
            Auth key from user if not set, the client auth key will be used
        Returns
        -------
        image_id: str
            ID of uploaded image
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `set_entity_image_local(self, entity_uri: str, path: pathlib.Path, auth_key: str | None = None) ‑> str`
    :   Setting the image of the entity.
        The image is stored locally.
        
        Parameters
        ----------
        entity_uri: str
           URI of the entity.
        path: Path
           The path of image.
        auth_key: Optional[str] [default:=None]
           Auth key from user if not set, the client auth key will be used
        
        Returns
        -------
        image_id: str
           ID of uploaded image
        
        Raises
        ------
        WacomServiceException
           If the graph service returns an error code.

    `set_entity_image_url(self, entity_uri: str, image_url: str, file_name: str | None = None, mime_type: str | None = None, auth_key: str | None = None) ‑> str`
    :   Setting the image of the entity.
        The image for the URL is downloaded and then pushed to the backend.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        entity_uri: str
            URI of the entity.
        image_url: str
            URL of the image.
        file_name: str [default:=None]
            Name of  the file. If None the name is extracted from URL.
        mime_type: str [default:=None]
            Mime type.
        auth_key: Optional[str] [default:=None]
            Auth key from user if not set, the client auth key will be used
        
        Returns
        -------
        image_id: str
            ID of uploaded image
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `update_entity(self, entity: knowledge.base.ontology.ThingObject, auth_key: str | None = None)`
    :   Updates entity in graph.
        
        Parameters
        ----------
        entity: ThingObject
            entity object
        auth_key: Optional[str]
            Use a different auth key than the one from the client
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code