Module knowledge.public.relations
=================================

Functions
---------

    
`wikidata_extractor_entities(qids: set[str]) ‑> dict[str, knowledge.public.wikidata.WikidataThing]`
:   Extracts an entity from Wikidata.
    
    Parameters
    ----------
    qids: set[str]
        Set of unique QIDs
    
    Returns
    -------
    wikidata_extractor: dict[str, WikidataThing]
        Wikidata map

    
`wikidata_relations_extractor(wikidata: dict[str, knowledge.public.wikidata.WikidataThing]) ‑> dict[str, list[dict[str, typing.Any]]]`
:   Extracts relations from Wikidata.
    
    Parameters
    ----------
    wikidata: dict[str, WikidataThing]
        Wikidata map
    
    Returns
    -------
    relations: dict[str, list[dict[str, Any]]]
        Relations map.