Module knowledge.ontomapping.manager
====================================

Functions
---------

    
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

    
`wikidata_to_thing(wikidata_thing: knowledge.public.wikidata.WikidataThing, all_relations: Dict[str, Any], supported_locales: List[str], pull_wikipedia: bool = False) ‑> knowledge.base.ontology.ThingObject`
:   Converts a Wikidata thing to a ThingObject.
    
    Parameters
    ----------
    wikidata_thing: WikidataThing
        Wikidata thing
    
    all_relations: Dict[str, Any]
        All relations.
    
    supported_locales: List[str]
        Supported locales.
    
    pull_wikipedia: bool
        Pull Wikipedia summary.
    
    Returns
    -------
    thing: ThingObject
        Thing object