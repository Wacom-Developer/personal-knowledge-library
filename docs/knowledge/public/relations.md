Module knowledge.public.relations
=================================

Functions
---------

    
`wikidata_extractor_entities(qids: Set[str]) ‑> Dict[str, knowledge.public.wikidata.WikidataThing]`
:   Extracts an entity from Wikidata.
    
    Parameters
    ----------
    qids: Set[str]
        Set of unique QIDs
    
    Returns
    -------
    wikidata_extractor: Dict[str, WikidataThing]
        Wikidata map

    
`wikidata_relations_extractor(wikidata: Dict[str, knowledge.public.wikidata.WikidataThing]) ‑> Dict[str, List[Dict[str, Any]]]`
: