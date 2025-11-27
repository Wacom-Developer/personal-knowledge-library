Module knowledge.nel.base
=========================

Classes
-------

`BasicNamedEntity(ref_text: str, start_idx: int, end_idx: int, basic_type: knowledge.nel.base.BasicType)`
:   Basic named entity
    ------------------
    Entity found by Named entity recognition.
    
    Parameters
    ----------
    ref_text: str
        Reference text. Entity found for this specific text
    start_idx: int
        Start index within the full reference text
    end_idx: int
        End index with the full reference text
    basic_type: BasicType
        Type of the entity.

    ### Ancestors (in MRO)

    * knowledge.nel.base.NamedEntity
    * abc.ABC

    ### Instance variables

    `basic_type: knowledge.nel.base.BasicType`
    :   Basic type that is recognized.

`BasicType(*args, **kwds)`
:   Enumeration representing basic types of entities.
    
    Defines a set of basic entity types used for categorization and identification
    in various contexts. This enumeration allows for easy comparison, clarity, and
    definition of specific categories for entities that can be encountered in
    different scenarios.
    
    Attributes
    ----------
    UNKNOWN : str
        Represents an unknown or undefined type.
    MONEY : str
        Represents a monetary value or currency-related type.
    PERSON : str
        Represents a person or an entity associated with a human being.
    DATE : str
        Represents a calendar date.
    PLACE : str
        Represents a physical or geographical location.
    TIME : str
        Represents a specific point in time or a duration.
    NUMBER : str
        Represents a numerical value or type.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `DATE`
    :

    `MONEY`
    :

    `NUMBER`
    :

    `PERSON`
    :

    `PLACE`
    :

    `TIME`
    :

    `UNKNOWN`
    :

`EntitySource(uri: str, source: knowledge.nel.base.KnowledgeSource)`
:   EntitySource
    ------------
    Source of the entity.
    
    Parameters
    ----------
    uri: str
        URI of entity
    source: KnowledgeSource
        Identifier where the entity originates.

    ### Instance variables

    `source: knowledge.nel.base.KnowledgeSource`
    :   Source of the entity.

    `uri: str`
    :   Identifier with the knowledge graph.

`EntityType(*args, **kwds)`
:   Represents different types of entities.
    
    This enumeration class categorizes entities into three distinct types: Public,
    Personal, and Named. These types help to identify whether the entity belongs
    to a globally accessible knowledge graph, a specific private knowledge source,
    or if it is a standalone named entity without a linkage to an external knowledge graph.
    
    Attributes
    ----------
    PUBLIC_ENTITY : int
        Public entity - Entity from a public knowledge graph.
    PERSONAL_ENTITY : int
        Personal entity - Entity from a personal or organizational knowledge
        graph.
    NAMED_ENTITY : int
        Simple entity - Entity type not linked to a knowledge graph.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `NAMED_ENTITY`
    :   Simple entity - Entity type not linked to a knowledge graph

    `PERSONAL_ENTITY`
    :   Personal entity - Entity from a personal / organisational knowledge graph

    `PUBLIC_ENTITY`
    :   Public entity - Entity from a public knowledge graph

`KnowledgeGraphEntity(ref_text: str, start_idx: int, end_idx: int, label: str, confidence: float, source: knowledge.nel.base.EntitySource, content_link: str, ontology_types: List[str], entity_type: knowledge.nel.base.EntityType = EntityType.PUBLIC_ENTITY, tokens: List[str] | None = None, token_indexes: List[int] | None = None)`
:   Knowledge graph entity
    ----------------------
    Entity from a knowledge graph.
    
    Parameters
    ----------
    ref_text: str
        Reference text. Entity found for this specific text
    start_idx: int
        Start index within the full reference text
    end_idx: int
        End index with the full reference text
    label: str
        Main label of the entity.
    confidence: float
        Confidence value if available
    source: EntitySource
        Source of the entity
    content_link: str
        Link to side with content
    ontology_types: List[str]
        List of ontology types (class names)
    entity_type: EntityType
        Type of the entity.
    tokens: Optional[List[str]] (default:=None)
        List of tokens used to identify the entity.
    token_indexes: Optional[List[int]] (default:=None)
        List of token indexes used to identify the entity.

    ### Ancestors (in MRO)

    * knowledge.nel.base.NamedEntity
    * abc.ABC

    ### Instance variables

    `confidence: float`
    :   Confidence level of the system that links the entities.

    `content_link: str`
    :   Link to content page.

    `description: str | None`
    :   Description of the entity if available.

    `entity_source: knowledge.nel.base.EntitySource`
    :   Source of the entity.

    `label: str`
    :   Label of the entity from the knowledge graph.

    `ontology_types: List[str]`
    :   List of ontology types.

    `relevant_type: knowledge.base.ontology.OntologyClassReference`
    :   Most relevant ontology type. That like to Wacom's personal knowledge base ontology.

    `thumbnail: str | None`
    :   Thumbnail to describe the entity.

    `token_indexes: List[int] | None`
    :   List of token indexes used to identify the entity.

    `tokens: List[str] | None`
    :   List of tokens used to identify the entity.

`KnowledgeSource(*args, **kwds)`
:   KnowledgeSource defines an enumeration for different knowledge sources.
    
    This enumeration lists predefined constants representing various sources
    of knowledge. It helps standardize and unify the representation of external
    knowledge systems used within an application. Each attribute corresponds
    to a specific knowledge source, represented as a string.
    
    Attributes
    ----------
    WIKIDATA : str
        Wikidata
    DBPEDIA : str
        dbpedia
    WACOM_KNOWLEDGE : str
        Wacom Personal Knowledge

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `DBPEDIA`
    :   dbpedia

    `WACOM_KNOWLEDGE`
    :   Wacom Personal Knowledge

    `WIKIDATA`
    :   Wikidata

`NamedEntity(ref_text: str, start_idx: int, end_idx: int, entity_type: knowledge.nel.base.EntityType)`
:   NamedEntity
    -----------
    A named entity which is recognized by the recognition engine.
    The class contains information on the found entity, found in reference text.
    
    Parameters
    ----------
    ref_text: str
        Reference text. Entity found for this specific text
    start_idx: int
        Start index within the full reference text
    end_idx: int
        End index with the full reference text
    entity_type: EntityType
        Type of the entity.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.nel.base.BasicNamedEntity
    * knowledge.nel.base.KnowledgeGraphEntity

    ### Instance variables

    `end_idx: int`
    :   End index within the text handed to the named entity recognition.

    `entity_type: knowledge.nel.base.EntityType`
    :   Type of the entity.

    `ref_text: str`
    :   Reference text for which the entity has been found

    `start_idx: int`
    :   Start an index within the text handed to the named entity recognition.

`NamedEntityRecognitionProcessor(service_url: str, supported_languages: List[knowledge.base.language.LocaleCode] = None, verify_calls: bool = False)`
:   NamedEntityRecognitionProcessor
    -------------------------------
    Service that recognizes entities.
    
    Parameters
    ----------
    service_url: str
        URL where the service has been deployed
    supported_languages: List[str] = None
        List of supported languages
    verify_calls: bool (default:=False)
        Verifies all HTTPS calls and the associated certificate.

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Instance variables

    `supported_language: List[knowledge.base.language.LocaleCode]`
    :   List of supported languages.

    ### Methods

    `is_language_supported(self, language_code: knowledge.base.language.LocaleCode) ‑> bool`
    :   Is the language_code code supported by the engine.
        
        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        
        Returns
        -------
        flag: bool
            Flag if this language_code code is supported

    `named_entities(self, text: str, language_code: knowledge.base.language.LocaleCode = 'en_US') ‑> List[knowledge.nel.base.NamedEntity]`
    :   Performs Named Entity Recognition on a text.
        
        Parameters
        ----------
        text: str
            Text where the entities shall be tagged in.
        language_code: LocaleCode (default:= 'en_US')
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        
        Returns
        -------
        entities: List[NamedEntity]
            List of knowledge named entities.

`PersonalEntityLinkingProcessor(service_url: str, application_name: str = 'Semantic Search Client', base_auth_url: str | None = None, service_endpoint: str = 'vector/api/v1', verify_calls: bool = True, max_retries: int = 3, backoff_factor: float = 0.1)`
:   PersonalEntityLinkingProcessor
    ------------------------------
    Service that links entities to entities in a personal knowledge graph.
    
    Parameters
    ----------
    service_url: str
        URL where the service has been deployed
    verify_calls: bool (default:=False)
        Verifies all HTTPS calls and the associated certificate.

    ### Ancestors (in MRO)

    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Descendants

    * knowledge.nel.engine.WacomEntityLinkingEngine

    ### Class variables

    `LANGUAGES: List[knowledge.base.language.LocaleCode]`
    :

    ### Instance variables

    `supported_language: List[str]`
    :   List of supported languages.

    ### Methods

    `is_language_supported(self, language_code: knowledge.base.language.LocaleCode) ‑> bool`
    :   Is the language_code code supported by the engine.
        
        Parameters
        -----------
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        
        Returns
        -------
        flag: bool
            Flag if this language_code code is supported.

    `link_personal_entities(self, text: str, language_code: knowledge.base.language.LocaleCode = 'en_US', auth_key: str | None = None, max_retries: int = 5) ‑> List[knowledge.nel.base.KnowledgeGraphEntity]`
    :   Performs Named Entity Linking on a text. It only finds entities which are accessible by the user identified by
        the auth key.
        
        Parameters
        ----------
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        auth_key: Optional[str] (default:=None)
            Auth key identifying a user within the Wacom personal knowledge service.
        max_retries: int (default:=5)
            Maximum number of retries, if the service is not available.
        Returns
        -------
        entities: List[KnowledgeGraphEntity]
            List of knowledge graph entities.

`PublicEntityLinkingProcessor(service_url: str, provider: str = 'external', supported_languages: List[str] = None, verify_calls: bool = False)`
:   Public Entity Linking
    ---------------------
    Service that links entities to a public entity in a knowledge graph.
    
    Parameters
    ----------
    service_url: str
        URL where the service has been deployed
    supported_languages: List[str] = None
        List of supported languages
    verify_calls: bool (default:=False)
        Verifies all HTTPS calls and the associated certificate.

    ### Ancestors (in MRO)

    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Instance variables

    `provider: str`
    :   Provider of the service.

    `supported_language: List[str]`
    :   List of supported languages.

    ### Methods

    `is_language_supported(self, language_code: knowledge.base.language.LocaleCode) ‑> bool`
    :   Is the language_code code supported by the engine.
        
        Parameters
        ----------
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        
        Returns
        -------
        flag: bool
            Flag if this language_code code is supported

    `link_public_entities(self, text: str, language_code: knowledge.base.language.LocaleCode = 'en_US') ‑> List[knowledge.nel.base.KnowledgeGraphEntity]`
    :   Performs Named Entity Linking on a text. It only finds entities within a large public knowledge graph.
        
        Parameters
        ----------
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., en_US.
        
        Returns
        -------
        entities: List[KnowledgeGraphEntity]
            List of public knowledge entities.