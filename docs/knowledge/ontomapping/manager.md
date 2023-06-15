Module knowledge.ontomapping.manager
====================================

Functions
---------

    
`convert_dict(structure: dict[str, typing.Any], locale: str) ‑> Optional[str]`
:   Converts a dictionary to a string.
    Parameters
    ----------
    structure:  dict[str, Any]
        Dictionary to convert.
    locale: str
        Locale.
    
    Returns
    -------
    string: str
        String representation of the dictionary.

    
`flatten(hierarchy: knowledge.public.wikidata.WikidataClass, use_names: bool = False) ‑> list[str]`
:   Flattens the hierarchy.
    
    Parameters
    ----------
    hierarchy: WikidataClass
        Hierarchy
    use_names: bool
        Use names instead of QIDs.
    
    Returns
    -------
    hierarchy: list[str]
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

    
`wikidata_to_thing(wikidata_thing: knowledge.public.wikidata.WikidataThing, all_relations: dict[str, typing.Any], supported_locales: list[str], all_wikidata_objects: dict[str, knowledge.public.wikidata.WikidataThing], pull_wikipedia: bool = False) ‑> tuple[knowledge.base.ontology.ThingObject, list[dict[str, typing.Any]]]`
:   Converts a Wikidata thing to a ThingObject.
    
    Parameters
    ----------
    wikidata_thing: WikidataThing
        Wikidata thing
    
    all_relations: dict[str, Any]
        All relations.
    
    supported_locales: list[str]
        Supported locales.
    
    all_wikidata_objects: dict[str, WikidataThing]
        All Wikidata objects.
    
    pull_wikipedia: bool
        Pull Wikipedia summary.
    
    Returns
    -------
    thing: ThingObject
        Thing object
    import_warnings: list[dict[str, Any]]
        Errors