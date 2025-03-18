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

`wikidata_relations_extractor(wikidata: Dict[str, knowledge.public.wikidata.WikidataThing], progress_relations: Callable[[int, int], None] | None = None) ‑> Dict[str, List[Dict[str, Any]]]`
:   Extracts relations from Wikidata.
    
    Parameters
    ----------
    wikidata: Dict[str, WikidataThing]
        Wikidata map
    progress_relations: Optional[Callable[[int, int], None]] = None
        Progress callback function.
    
    Returns
    -------
    relations: Dict[str, List[Dict[str, Any]]]
        Relations map.

`wikidata_relations_extractor_qids(wikidata: Dict[str, knowledge.public.wikidata.WikidataThing], qids: Set[str]) ‑> Dict[str, List[Dict[str, Any]]]`
:   Extracts relations from Wikidata.
    
    Parameters
    ----------
    wikidata: Dict[str, WikidataThing]
        Wikidata map
    qids: Set[str]
        Set of unique QIDs
    
    Returns
    -------
    relations: Dict[str, List[Dict[str, Any]]]
        Relations map.