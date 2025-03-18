Module knowledge.utils.wikidata
===============================

Functions
---------

`build_query(params: Dict[str, Any]) ‑> List[str]`
:   Build of query.
    
    Parameters
    ----------
    params:
        Parameters for query
    
    Returns
    -------
    queries: List[str]
        SPARQL query string

`extract_qid(url: str) ‑> str`
:   Extract qid from url.
    Parameters
    ----------
    url: str
        URL
    
    Returns
    -------
    qid: str
        QID

`from_dict(entity: Dict[str, Any], concept_type: knowledge.base.ontology.OntologyClassReference) ‑> knowledge.base.ontology.ThingObject`
:   Create a thing object from a dictionary.
    Parameters
    ----------
    entity: Dict[str, Any]
        Entities dictionary.
    concept_type: OntologyClassReference
        Concept type.
    
    Returns
    -------
    thing: ThingObject
        Thing object.

`localized_flatten_alias_list(entity_dict: Dict[str, List[str]]) ‑> List[knowledge.base.entity.Label]`
:   Flattens the alias list.
    Parameters
    ----------
    entity_dict: Dict[str, List[str]]
        Entities dictionary.
    
    Returns
    -------
    flatten: List[Label]
        Flattened list of labels.

`localized_list_description(entity_dict: Dict[str, str]) ‑> List[knowledge.base.entity.Description]`
:   Creates a list of descriptions for the given entity dictionary.
    Parameters
    ----------
    entity_dict: Dict[str, str]
        Entities dictionary.
    
    Returns
    -------
    descriptions: List[Description]
        List of descriptions.

`localized_list_label(entity_dict: Dict[str, str]) ‑> List[knowledge.base.entity.Label]`
:   Creates a list of labels for the given entity dictionary.
    
    Parameters
    ----------
    entity_dict: Dict[str, str]
        Entities dictionary.
    
    Returns
    -------
    labels: List[Label]
        List of labels.

`strip(url: str) ‑> str`
:   Strip qid from url.
    Parameters
    ----------
    url: str
        URL
    Returns
    -------
    result: str
        Stripped URL

`update_language_code(lang: knowledge.base.language.LanguageCode) ‑> knowledge.base.language.LocaleCode`
:   Update the language_code code to a default language_code / country code
    Parameters
    ----------
    lang: LanguageCode
        Language code.
    
    Returns
    -------
    language_code: LocaleCode
        Language code.
    
    Raises
    ------
    ValueError
        If the language_code code is not supported.