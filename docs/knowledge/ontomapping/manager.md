Module knowledge.ontomapping.manager
====================================

Functions
---------

    
`convert_dict(structure: Dict[str, Any], locale: str) ‑> Optional[str]`
:   Converts a dictionary to a string.
    Parameters
    ----------
    structure:  Dict[str, Any]
        Dictionary to convert.
    locale: str
        Locale.
    
    Returns
    -------
    string: str
        String representation of the dictionary.

    
`flatten(hierarchy: knowledge.public.wikidata.WikidataClass, use_names: bool = False) ‑> List[str]`
:   Flattens the hierarchy.
    
    Parameters
    ----------
    hierarchy: WikidataClass
        Hierarchy
    use_names: bool
        Use names instead of QIDs.
    
    Returns
    -------
    hierarchy: List[str]
        Hierarchy

    
`wikidata_taxonomy(qid: str) ‑> Optional[knowledge.public.wikidata.WikidataClass]`
:   Returns the taxonomy of a Wikidata thing.
    Parameters
    ----------
    qid: str
        Wikidata QID.
    
    Returns
    -------
    hierarchy: WikidataClass
        Hierarchy.

    
`wikidata_to_thing(wikidata_thing: knowledge.public.wikidata.WikidataThing, all_relations: Dict[str, Any], supported_locales: List[str], all_wikidata_objects: Dict[str, knowledge.public.wikidata.WikidataThing], pull_wikipedia: bool = False, guess_concept_type: bool = True) ‑> Tuple[knowledge.base.ontology.ThingObject, List[Dict[str, Any]]]`
:   Converts a Wikidata thing to a ThingObject.
    
    Parameters
    ----------
    wikidata_thing: WikidataThing
        Wikidata thing
    
    all_relations: Dict[str, Any]
        All relations.
    
    supported_locales: List[str]
        Supported locales.
    
    all_wikidata_objects: Dict[str, WikidataThing]
        All Wikidata objects.
    
    pull_wikipedia: bool
        Pull Wikipedia summary.
    
    guess_concept_type: bool
        Guess the concept type (queries all super types from Wikidata).
    
    Returns
    -------
    thing: ThingObject
        Thing object
    import_warnings: List[Dict[str, Any]]
        Errors