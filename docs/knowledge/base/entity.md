Module knowledge.base.entity
============================

Classes
-------

`Comment(text: str, language_code: LanguageCode = 'en')`
:   Comment
    -------
    Comment that is multi-lingual.
    
    Parameters
    ----------
    text: str
        Text value
    language_code: LanguageCode (default:= 'en')
        Language code of content

    ### Ancestors (in MRO)

    * knowledge.base.entity.LocalizedContent
    * abc.ABC

    ### Static methods

    `create_from_dict(dict_description: Dict[str, Any]) ‑> knowledge.base.entity.Comment`
    :

    `create_from_list(param: List[Dict[str, Any]]) ‑> List[knowledge.base.entity.Comment]`
    :

`Description(description: str, language_code: LanguageCode = 'en_US')`
:   Description
    -----------
    Description that is multi-lingual.
    
    Parameters
    ----------
    description: str
        Description value
    language_code: LanguageCode (default:= 'en_US')
        Language code of content

    ### Ancestors (in MRO)

    * knowledge.base.entity.LocalizedContent
    * abc.ABC

    ### Static methods

    `create_from_dict(dict_description: Dict[str, Any]) ‑> knowledge.base.entity.Description`
    :

    `create_from_list(param: List[Dict[str, Any]]) ‑> List[knowledge.base.entity.Description]`
    :

`EntityStatus(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Entity Status
    -------------
    Status of the entity synchronization (client and knowledge graph).

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CREATED`
    :   Entity has been created and not yet update.

    `SYNCED`
    :   State of entity is in sync with knowledge graph.

    `UNKNOWN`
    :   Unknown status.

    `UPDATED`
    :   Entity has been updated by the client and must be synced.

`KnowledgeException(*args, **kwargs)`
:   Knowledge exception.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`Label(content: str, language_code: LanguageCode = 'en_US', main: bool = False)`
:   Label
    -----
    Label that is multi-lingual.
    
    Parameters
    ----------
    content: str
        Content value
    language_code: LanguageCode (default:= 'en_US')
        Language code of content
    main: bool (default:=False)
        Main content

    ### Ancestors (in MRO)

    * knowledge.base.entity.LocalizedContent
    * abc.ABC

    ### Static methods

    `create_from_dict(dict_label: Dict[str, Any], tag_name: str = 'value', locale_name: str = 'locale') ‑> knowledge.base.entity.Label`
    :

    `create_from_list(param: List[dict]) ‑> List[knowledge.base.entity.LocalizedContent]`
    :

    ### Instance variables

    `main: bool`
    :   Flag if the content is the  main content or an alias.

`LocalizedContent(content: str, language_code: LanguageCode = 'en_US')`
:   Localized content
    -----------------
    Content that is multi-lingual.
    
    Parameters
    ----------
    content: str
        Content value
    language_code: LanguageCode (default:= 'en_US')
        ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>, e.g., en_US.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.base.entity.Comment
    * knowledge.base.entity.Description
    * knowledge.base.entity.Label
    * knowledge.base.entity.OntologyLabel

    ### Instance variables

    `content: str`
    :   String representation of the content.

    `language_code: LanguageCode`
    :   Language code of the content.

`OntologyContext(cid: str, tenant_id: str, name: str, icon: str, labels: List[knowledge.base.entity.Label], comments: List[knowledge.base.entity.Comment], date_added: datetime.datetime, date_modified: datetime.datetime, context: str, base_uri: str, version: int, orphaned: bool, concepts: List[str], properties: List[str])`
:   OntologyContext
    ----------------
    Ontology context representation.
    
    Parameters
    ----------
    cid: str
        Context id
    tenant_id: str
        Tenant id.
    name: str
        Name of the ontology context
    icon: str
        Icon or Base64 encoded
    labels: List[Label]
        List of labels
    comments: List[Comment]
        List of comments
    context: str
        context name
    base_uri: str
        Base URI
    concepts: List[str]
        List of classes / concepts
    properties: List[str]
        List of properties (data and object properties)

    ### Ancestors (in MRO)

    * knowledge.base.entity.OntologyObject
    * abc.ABC

    ### Static methods

    `from_dict(context_dict: Dict[str, Any])`
    :

    ### Instance variables

    `base_uri: str`
    :

    `id: str`
    :

    `orphaned: bool`
    :

`OntologyContextSettings(rdf_prefix: str, rdfs_prefix: str, owl_prefix: str, base_literal_uri: str, base_class_uri: str, description_literal_name: str, depth: int)`
:   OntologyContextSettings
    -----------------------
    Describes the settings of the context, such as:
    - prefixes for RDF, RDFS and OWL
    - Base literal URI
    - Base class URI
    - Description literal name
    - depth

    ### Instance variables

    `base_class_uri`
    :   Base class URI.

    `base_literal_uri`
    :   Base literal URI.

    `depth: int`
    :   Depth.

    `description_literal_name: str`
    :   Literal name of the description.

    `owl_prefix`
    :   OWL prefix

    `rdf_prefix`
    :   RDF prefix

    `rdfs_prefix`
    :   RDFS prefix

`OntologyLabel(content: str, language_code: LanguageCode = 'en', main: bool = False)`
:   Ontology Label
    --------------
    Label that is multi-lingual.
    
    Parameters
    ----------
    content: str
        Content value
    language_code: LanguageCode (default:= 'en')
        Language code of content
    main: bool (default:=False)
        Main content

    ### Ancestors (in MRO)

    * knowledge.base.entity.LocalizedContent
    * abc.ABC

    ### Static methods

    `create_from_dict(dict_label: Dict[str, Any], tag_name: str = 'value', locale_name: str = 'locale') ‑> knowledge.base.entity.OntologyLabel`
    :

    `create_from_list(param: List[dict]) ‑> List[knowledge.base.entity.LocalizedContent]`
    :

    ### Instance variables

    `main: bool`
    :   Flag if the content is the  main content or an alias.

`OntologyObject(tenant_id: str, iri: str, icon: str, labels: List[knowledge.base.entity.OntologyLabel], comments: List[knowledge.base.entity.Comment], context: str)`
:   Generic ontology object
    -----------------------
    
    Parameters
    ----------
    tenant_id: str
        Reference id for tenant
    iri: str
        IRI of the ontology object
    icon: str
        Icon assigned to object, visually representing it
    labels: List[Label]
        List of multi-language_code labels
    comments: List[Label]
        List of multi-language_code comments
    context: str
        Context

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.base.entity.OntologyContext
    * knowledge.base.ontology.OntologyClass
    * knowledge.base.ontology.OntologyProperty

    ### Instance variables

    `comments: List[knowledge.base.entity.Comment]`
    :   Comment related to ontology object.

    `context: str`
    :   Context.

    `icon: str`
    :   Icon.

    `iri: str`
    :   IRI

    `labels: List[knowledge.base.entity.OntologyLabel]`
    :

    `tenant_id: str`
    :   Tenant id.

    ### Methods

    `comment_for_lang(self, language_code: LanguageCode) ‑> Optional[knowledge.base.entity.Comment]`
    :

    `label_for_lang(self, language_code: LanguageCode) ‑> Optional[knowledge.base.entity.OntologyLabel]`
    :

`ServiceException(*args, **kwargs)`
:   Service exception.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException