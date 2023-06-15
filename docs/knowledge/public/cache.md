Module knowledge.public.cache
=============================

Functions
---------

    
`cache_wikidata_object(wikidata_object: knowledge.public.wikidata.WikidataThing)`
:   Caches a Wikidata object.
    Parameters
    ----------
    wikidata_object: WikidataObject
        The Wikidata object

    
`cache_wikidata_objects() ‑> Dict[str, knowledge.public.wikidata.WikidataThing]`
:   Returns the Wikidata cache.
    Returns
    -------
    wikidata_cache: Dict[str, WikidataThing]
        Wikidata cache.

    
`get_wikidata_object(qid_object: str) ‑> knowledge.public.wikidata.WikidataThing`
:   Returns a Wikidata object from the cache.
    
    Parameters
    ----------
    qid_object: str
        The QID of the Wikidata object.
    Returns
    -------
    wikidata_object: WikidataThing
        The Wikidata object.

    
`load_cache(cache: pathlib.Path)`
:   Load the cache from the file.
    Parameters
    ----------
    cache: Path
        Path to the cache file.

    
`number_of_cached_objects() ‑> int`
:   Returns the number of cached objects.
    Returns
    -------
    number_of_cached_objects: int
        Number of cached objects.

    
`pull_wikidata_object(qid_object: str) ‑> Optional[knowledge.public.wikidata.WikidataThing]`
:   Pulls a Wikidata object from the cache or from the Wikidata API.
    Parameters
    ----------
    qid_object: str
        The QID of the Wikidata object.
    Returns
    -------
    wikidata_object: Optional[WikidataThing]
        The Wikidata object, if it exists, otherwise None.

    
`qid_in_cache(ref_qid: str) ‑> bool`
:   Checks if a QID is in the cache.
    Parameters
    ----------
    ref_qid: str
        The QID to check.
    
    Returns
    -------
    in_cache: bool
        True if the QID is in the cache, otherwise False.