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

`BasicType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Basic type
    ----------
    Basic type of entities.

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

`EntityType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Entity types
    ------------
    Different types of entities.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `NAMED_ENTITY`
    :   Simple entity - Entity type not linked to a knowledge graph

    `PERSONAL_ENTITY`
    :   Personal entity - Entity from a personal / organisational knowledge graph

    `PUBLIC_ENTITY`
    :   Public entity - Entity from a public knowledge graph

`KnowledgeGraphEntity(ref_text: str, start_idx: int, end_idx: int, label: str, confidence: float, source: knowledge.nel.base.EntitySource, content_link: str, ontology_types: List[str], entity_type: knowledge.nel.base.EntityType = EntityType.PUBLIC_ENTITY)`
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

    ### Ancestors (in MRO)

    * knowledge.nel.base.NamedEntity
    * abc.ABC

    ### Instance variables

    `confidence: float`
    :   Confidence level of the system that links the entities.

    `content_link: str`
    :   Link to content page.

    `description: Optional[str]`
    :   Description of the entity if available.

    `entity_source: knowledge.nel.base.EntitySource`
    :   Source of the entity.

    `label: str`
    :   Label of the entity from the knowledge graph.

    `ontology_types: List[str]`
    :   List of ontology types.

    `relevant_type: knowledge.base.ontology.OntologyClassReference`
    :   "Most relevant ontology type. That likes to Wacom's personal knowledge base ontology.

    `thumbnail: Optional[str]`
    :   Thumbnail to describes the entity.

`KnowledgeSource(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Knowledge source
    ----------------
    List of knowledge sources which a used within Semantic Ink.

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
    A named entity which is recognized by recognition engine.
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
    :   Start index within the text handed to the named entity recognition.

`NamedEntityRecognitionProcessor(service_url: str, supported_languages: List[knowledge.base.entity.LanguageCode] = None, verify_calls: bool = False)`
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

    `supported_language: List[knowledge.base.entity.LanguageCode]`
    :   List of supported languages.

    ### Methods

    `is_language_supported(self, language_code: knowledge.base.entity.LanguageCode) ‑> bool`
    :   Is the language_code code supported by the engine.
        
        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        
        Returns
        -------
        flag: bool
            Flag if this language_code code is supported

    `named_entities(self, text: str, language_code: knowledge.base.entity.LanguageCode = 'en_US') ‑> List[knowledge.nel.base.NamedEntity]`
    :   Performs Named Entity Recognition on a text.
        
        Parameters
        ----------
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        
        Returns
        -------
        entities: List[NamedEntity]
            List of knowledge named entities.

`PersonalEntityLinkingProcessor(service_url: str = builtins.str, supported_languages: List[str] = None, verify_calls: bool = True)`
:   PersonalEntityLinkingProcessor
    ------------------------------
    Service that links entities to a entities in a personal knowledge graph.
    
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

    ### Descendants

    * knowledge.nel.engine.WacomEntityLinkingEngine

    ### Instance variables

    `supported_language: List[str]`
    :   List of supported languages.

    ### Methods

    `is_language_supported(self, language_code: knowledge.base.entity.LanguageCode) ‑> bool`
    :   Is the language_code code supported by the engine.
        
        Parameters
        -----------
        language_code: str
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        
        Returns
        -------
        flag: bool
            Flag if this language_code code is supported.

    `link_personal_entities(self, auth_key: str, text: str, language_code: knowledge.base.entity.LanguageCode = 'en_US') ‑> List[knowledge.nel.base.KnowledgeGraphEntity]`
    :   Performs Named Entity Linking on a text. It only finds entities which are accessible by the user identified by
        the auth key.
        
        Parameters
        ----------
        auth_key: str
            Auth key identifying a user within the Wacom personal knowledge service.
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        
        Returns
        -------
        entities: List[KnowledgeGraphEntity]
            List of knowledge graph entities.

`PublicEntityLinkingProcessor(service_url: str = builtins.str, supported_languages: List[str] = None, verify_calls: bool = False)`
:   Public Entity Linking
    ---------------------
    Service that links entities to a public entities in a knowledge graph.
    
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

    `supported_language: List[str]`
    :   List of supported languages.

    ### Methods

    `is_language_supported(self, language_code: str) ‑> bool`
    :   Is the language_code code supported by the engine.
        
        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        
        Returns
        -------
        flag: bool
            Flag if this language_code code is supported

    `link_public_entities(self, text: str, language_code: knowledge.base.entity.LanguageCode = 'en_US') ‑> List[knowledge.nel.base.KnowledgeGraphEntity]`
    :   Performs Named Entity Linking on a text. It only finds entities within a large public knowledge graph.
        
        Parameters
        ----------
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.
        
        Returns
        -------
        entities: List[KnowledgeGraphEntity]
            List of knowledge public knowledge entities.