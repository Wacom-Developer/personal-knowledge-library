Module knowledge.services.graph
===============================

Classes
-------

`SearchPattern(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   SearchPattern
    -------------
    Different search pattern for literal search.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `EQ`
    :   Equal search pattern.

    `GT`
    :   Greater than search pattern.

    `GTE`
    :   Greater than or equal search pattern.

    `LT`
    :   Less than search pattern.

    `LTE`
    :   Less than or equal search pattern.

    `RANGE`
    :   Range search pattern.

    `REGEX`
    :   Regular expression search pattern.

`Visibility(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Visibility
    ----------
    Visibility of an entity.
    The visibility of an entity determines who can see the entity.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `PRIVATE`
    :   Only the owner of the entity can see the entity.

    `PUBLIC`
    :   Everyone in the tenant can see the entity.

    `SHARED`
    :   Everyone who joined the group can see the entity.

`WacomKnowledgeService(application_name: str, service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph/v1')`
:   WacomKnowledgeService
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
        Name of the application using the service
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
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

    `activations(self, auth_key: str, uris: list[str], depth: int) ‑> tuple[dict[str, knowledge.base.ontology.ThingObject], list[tuple[str, knowledge.base.ontology.OntologyPropertyReference, str]]]`
    :   Spreading activation, retrieving the entities related to an entity.
        
        Parameters
        ----------
        auth_key: str
            Auth key for user
        uris: list[str]
            List of URIS for entity.
        depth: int
            Depth of activations
        
        Returns
        -------
        entity_map: dict[str, ThingObject]
            Map with entity and its URI as key.
        relations: list[tuple[str, OntologyPropertyReference, str]]
            List of relations with subject predicate, (Property), and subject
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code, and activation failed.

    `create_entity(self, auth_key: str, entity: knowledge.base.ontology.ThingObject, max_retries: int = 3, backoff_factor: float = 0.1, ignore_image: bool = False) ‑> str`
    :   Creates entity in graph.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        entity: ThingObject
            Entity object that needs to be created
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
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

    `create_entity_bulk(self, auth_key: str, entities: list[knowledge.base.ontology.ThingObject], batch_size: int = 10) ‑> list[knowledge.base.ontology.ThingObject]`
    :   Creates entity in graph.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        entities: list[ThingObject]
            Entities
        batch_size: int
            Batch size
        
        Returns
        -------
        uri: str
            URI of entity
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `create_relation(self, auth_key: str, source: str, relation: knowledge.base.ontology.OntologyPropertyReference, target: str)`
    :   Creates a relation for an entity to a source entity.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        source: str
            Entity URI of the source
        relation: OntologyPropertyReference
            ObjectProperty property
        target: str
            Entity URI of the target
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `delete_entities(self, auth_key: str, uris: list[str], force: bool = False, max_retries: int = 3, backoff_factor: float = 0.1)`
    :   Delete a list of entities.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        uris: list[str]
            List of URI of entities. **Remark:** More than 100 entities are not possible in one request
        force: bool
            Force deletion process
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `delete_entity(self, auth_key: str, uri: str, force: bool = False, max_retries: int = 3, backoff_factor: float = 0.1)`
    :   Deletes an entity.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        uri: str
            URI of entity
        force: bool
            Force deletion process
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `entity(self, auth_key: str, uri: str) ‑> knowledge.base.ontology.ThingObject`
    :   Retrieve entity information from personal knowledge, using the  URI as identifier.
        
        **Remark:** Object properties (relations) must be requested separately.
        
        Parameters
        ----------
        auth_key: str
            Auth key identifying a user within the Wacom personal knowledge service.
        uri: str
            URI of entity
        
        Returns
        -------
        thing: ThingObject
            Entity with is type URI, description, an image/icon, and tags (labels).
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code or the entity is not found in the knowledge graph

    `exists(self, auth_key: str, uri: str) ‑> bool`
    :   Check if entity exists in knowledge graph.
        
        Parameters
        ----------
        auth_key: str -
            User token
        uri: str -
            URI for entity
        
        Returns
        -------
        flag: bool
            Flag if entity does exist

    `labels(self, auth_key: str, uri: str, locale: str = 'en_US') ‑> list[knowledge.base.entity.Label]`
    :   Extract list labels of entity.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        uri: str
            Entity URI of the source
        locale: str
            ISO-3166 Country Codes and ISO-639 Language Codes in the format <language_code>_<country>, e.g., en_US.
        
        Returns
        -------
        labels: list[Label]
            List of labels of an entity.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `listing(self, auth_key: str, filter_type: knowledge.base.ontology.OntologyClassReference, page_id: Optional[str] = None, limit: int = 30, locale: Optional[knowledge.base.entity.LanguageCode] = None, visibility: Optional[knowledge.services.graph.Visibility] = None, estimate_count: bool = False, max_retries: int = 3, backoff_factor: float = 0.1) ‑> tuple[list[knowledge.base.ontology.ThingObject], int, str]`
    :   List all entities visible to users.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        filter_type: OntologyClassReference
            Filtering with entity
        page_id: Optional[str]
            Page id. Start from this page id
        limit: int
            Limit of the returned entities.
        locale: Optional[LanguageCode] [default:=None]
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        visibility: Optional[Visibility] [default:=None]
            Filter the entities based on its visibilities
        estimate_count: bool [default:=False]
            Request an estimate of the entities in a tenant.
        max_retries: int
            Maximum number of retries
        backoff_factor: float
            A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a
            second try without a delay)
        
        Returns
        -------
        entities: list[ThingObject]
            List of entities
        estimated_total_number: int
            Number of all entities
        next_page_id: str
            Identifier of the next page
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `literals(self, auth_key: str, uri: str, locale: str = 'en_US') ‑> list[knowledge.base.ontology.DataProperty]`
    :   Collect all literals of entity.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        uri: str
            Entity URI of the source
        locale: str
            ISO-3166 Country Codes and ISO-639 Language Codes in the format <language_code>_<country>, e.g., en_US.
        
        Returns
        -------
        labels: list[DataProperty]
            List of data properties of an entity.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `ontology_update(self, auth_key: str)`
    :   Update the ontology.
        
        **Remark:**
        Works for users with role 'TenantAdmin'.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code and commit failed.

    `relations(self, auth_key: str, uri: str) ‑> dict[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.ObjectProperty]`
    :   Retrieve the relations (object properties) of an entity.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        uri: str
            Entity URI of the source
        
        Returns
        -------
        relations: dict[OntologyPropertyReference, ObjectProperty]
            All relations a dict
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `remove_relation(self, auth_key: str, source: str, relation: knowledge.base.ontology.OntologyPropertyReference, target: str)`
    :   Removes a relation.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        source: str
            Entity uri of the source
        relation: OntologyPropertyReference
            ObjectProperty property
        target: str
            Entity uri of the target
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code

    `search_all(self, auth_key: str, search_term: str, language_code: knowledge.base.entity.LanguageCode, types: list[knowledge.base.ontology.OntologyClassReference], limit: int = 30, next_page_id: str = None) ‑> tuple[list[knowledge.base.ontology.ThingObject], str]`
    :   Search term in labels, literals and description.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        search_term: str
            Search term.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        types: list[OntologyClassReference]
            Limits the types for search.
        limit: int  (default:= 30)
            Size of the page for pagination.
        next_page_id: str (default:=None)
            ID of the next page within pagination.
        
        Returns
        -------
        results: list[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `search_description(self, auth_key: str, search_term: str, language_code: knowledge.base.entity.LanguageCode, limit: int = 30, next_page_id: str = None) ‑> tuple[list[knowledge.base.ontology.ThingObject], str]`
    :   Search for matches in description.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        search_term: str
            Search term.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        limit: int  (default:= 30)
            Size of the page for pagination.
        next_page_id: str (default:=None)
            ID of the next page within pagination.
        
        Returns
        -------
        results: list[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `search_labels(self, auth_key: str, search_term: str, language_code: knowledge.base.entity.LanguageCode, limit: int = 30, next_page_id: str = None) ‑> tuple[list[knowledge.base.ontology.ThingObject], str]`
    :   Search for matches in labels.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        search_term: str
            Search term.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        limit: int  (default:= 30)
            Size of the page for pagination.
        next_page_id: str (default:=None)
            ID of the next page within pagination.
        
        Returns
        -------
        results: list[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `search_literal(self, auth_key: str, search_term: str, literal: knowledge.base.ontology.OntologyPropertyReference, pattern: knowledge.services.graph.SearchPattern = SearchPattern.REGEX, language_code: knowledge.base.entity.LanguageCode = 'en_US', limit: int = 30, next_page_id: str = None) ‑> tuple[list[knowledge.base.ontology.ThingObject], str]`
    :   Search for matches in literals.
        
         Parameters
         ----------
         auth_key: str
             Auth key from user
         search_term: str
             Search term.
         literal: OntologyPropertyReference
             Literal used for the search
         pattern: SearchPattern (default:= SearchPattern.REGEX)
             Search pattern. The chosen search pattern must fit the type of the entity.
         language_code: LanguageCode
             ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
         limit: int (default:= 30)
             Size of the page for pagination.
         next_page_id: str (default:=None)
             ID of the next page within pagination.
        
         Returns
         -------
         results: list[ThingObject]
            List of things matching the search term
        next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `search_relation(self, auth_key: str, relation: knowledge.base.ontology.OntologyPropertyReference, language_code: knowledge.base.entity.LanguageCode, subject_uri: str = None, object_uri: str = None, limit: int = 30, next_page_id: str = None) ‑> tuple[list[knowledge.base.ontology.ThingObject], str]`
    :   Search for matches in literals.
        
         Parameters
         ----------
         auth_key: str
             Auth key from user
         relation: OntologyPropertyReference
             Search term.
         language_code: LanguageCode
             ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
         subject_uri: str (default:=None)
             URI of the subject
         object_uri: str (default:=None)
             URI of the object
         limit: int (default:= 30)
             Size of the page for pagination.
         next_page_id: str (default:=None)
             ID of the next page within pagination.
        
         Returns
         -------
         results: list[ThingObject]
            List of things matching the search term
         next_page_id: str
            ID of the next page.
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `set_entity_image(self, auth_key: str, entity_uri: str, image_byte: bytes, file_name: str = 'icon.jpg', mime_type: str = 'image/jpeg') ‑> str`
    :   Setting the image of the entity.
        The image for the URL is downloaded and then pushed to the backend.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        entity_uri: str
            URI of the entity.
        image_byte: bytes
            Binary encoded image.
        file_name: str (default:=None)
            Name of  the file. If None the name is extracted from URL.
        mime_type: str (default:=None)
            Mime type.
        
        Returns
        -------
        image_id: str
            ID of uploaded image
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `set_entity_image_local(self, auth_key: str, entity_uri: str, path: pathlib.Path) ‑> str`
    :   Setting the image of the entity.
        The image is stored locally.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        entity_uri: str
            URI of the entity.
        path: Path
            The path of image.
        
        Returns
        -------
        image_id: str
            ID of uploaded image
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `set_entity_image_url(self, auth_key: str, entity_uri: str, image_url: str, file_name: Optional[str] = None, mime_type: Optional[str] = None) ‑> str`
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
        file_name: str (default:=None)
            Name of  the file. If None the name is extracted from URL.
        mime_type: str (default:=None)
            Mime type.
        
        Returns
        -------
        image_id: str
            ID of uploaded image
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code.

    `update_entity(self, auth_key: str, entity: knowledge.base.ontology.ThingObject)`
    :   Updates entity in graph.
        
        Parameters
        ----------
        auth_key: str
            Auth key from user
        entity: ThingObject
            entity object
        
        Raises
        ------
        WacomServiceException
            If the graph service returns an error code