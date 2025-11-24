Module knowledge.public.client
==============================

Functions
---------

`chunks(lst: List[str], chunk_size: int)`
:   Yield successive n-sized chunks from lst.Yield successive n-sized chunks from lst.
    Parameters
    ----------
    lst: List[str]
        Full length.
    chunk_size: int
        Chunk size.

Classes
-------

`WikiDataAPIClient()`
:   WikiDataAPIClient
    -----------------
    Utility class for the WikiData.

    ### Static methods

    `retrieve_entities(qids: List[str] | Set[str], progress: Callable[[int, int], None] | None = None) ‑> List[knowledge.public.wikidata.WikidataThing]`
    :   Retrieve multiple Wikidata things.
        Parameters
        ----------
        qids: List[str]
            QIDs of the entities.
        progress: Optional[Callable[[int, int], None]]
            Optional callback function to report progress.
        
        Returns
        -------
        instances: List[WikidataThing]
            List of wikidata things.

    `retrieve_entity(qid: str) ‑> knowledge.public.wikidata.WikidataThing`
    :   Retrieve a single Wikidata thing.
        
        Parameters
        ----------
        qid: str
            QID of the entity.
        
        Returns
        -------
        instance: WikidataThing
            Single wikidata thing

    `search_term(search_term: str, language: knowledge.base.language.LanguageCode, url: str = 'https://www.wikidata.org/w/api.php') ‑> List[knowledge.public.wikidata.WikidataSearchResult]`
    :   Search for a term in the WikiData.
        Parameters
        ----------
        search_term: str
            The term to search for.
        language: str
            The language to search in.
        url: str
            The URL of the WikiData search API.
        
        Returns
        -------
        search_results_dict: List[WikidataSearchResult]
            The search results.

    `sparql_query(query_string: str, wikidata_sparql_url: str = 'https://query.wikidata.org/sparql', max_retries: int = 3) ‑> dict`
    :   Send a SPARQL query and return the JSON formatted result.
        
        Parameters
        -----------
        query_string: str
          SPARQL query string
        wikidata_sparql_url: str
          Wikidata SPARQL endpoint to use
        max_retries: int
            Maximum number of retries

    `subclasses(qid: str) ‑> Dict[str, knowledge.public.wikidata.WikidataClass]`
    :   Returns the Wikidata class with all its subclasses for the given QID.
        
        Parameters
        ----------
        qid: str
            Wikidata QID (e.g., 'Q146' for house cat).
        
        Returns
        -------
        classes: Dict[str, WikidataClass]
            A dictionary of WikidataClass objects, where the keys are QIDs and the values are the corresponding
            classes with their subclasses populated.

    `superclasses(qid: str) ‑> Dict[str, knowledge.public.wikidata.WikidataClass]`
    :   Returns the Wikidata class with all its superclasses for the given QID.
        
        Parameters
        ----------
        qid: str
            Wikidata QID (e.g., 'Q146' for house cat).
        
        Returns
        -------
        classes: Dict[str, WikidataClass]
            A dictionary of WikidataClass objects, where the keys are QIDs and the values are the corresponding

    `wikiproperty(pid: str) ‑> knowledge.public.wikidata.WikidataProperty`
    :   Retrieve a single Wikidata property.
        
        Parameters
        ----------
        pid: str
            PID of the property.
        
        Returns
        -------
        instance: WikidataProperty
            Single wikidata property