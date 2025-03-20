Module knowledge.public.cache
=============================

Functions
---------

`singleton(cls)`
:   Singleton decorator to ensure that a class has only one instance and provide a global point of access to it.

Classes
-------

`WikidataCache(max_size: int = 10000)`
:   WikidataCache
    --------------
    A singleton class that manages a cache of Wikidata objects using an LRU (Least Recently Used) strategy.
    
    Parameters
    ----------
    max_size: int
        The maximum size of the cache. When the cache exceeds this size, the least recently used item will be removed.
    
    Attributes
    ----------
    cache: OrderedDict
        The cache that stores Wikidata objects.

    ### Methods

    `cache_property(self, prop: knowledge.public.wikidata.WikidataProperty)`
    :   Adds a property to the property cache with LRU eviction.
        
        Parameters
        ----------
        prop: Dict[str, Any]
            The property to cache.

    `cache_subclass(self, subclass: knowledge.public.wikidata.WikidataClass)`
    :   Adds a subclass to the subclass cache with LRU eviction.
        
        Parameters
        ----------
        subclass: WikidataClass
            The subclass to cache.

    `cache_superclass(self, superclass: knowledge.public.wikidata.WikidataClass)`
    :   Adds a superclass to the superclass cache with LRU eviction.
        
        Parameters
        ----------
        superclass: WikidataClass
            The superclass to cache.

    `cache_wikidata_object(self, wikidata_object: knowledge.public.wikidata.WikidataThing)`
    :   Adds a Wikidata object to the cache with LRU eviction.
        
        Parameters
        ----------
        wikidata_object: WikidataThing
            The Wikidata object to cache.

    `get_property(self, pid: str) ‑> knowledge.public.wikidata.WikidataProperty`
    :   Retrieves a property from the property cache.
        
        Parameters
        ----------
        pid: str
            The PID of the property to retrieve.
        
        Returns
        -------
        Dict[str, Any]
            The property associated with the given PID.

    `get_subclass(self, qid: str) ‑> knowledge.public.wikidata.WikidataClass`
    :   Retrieves a subclass from the subclass cache.
        
        Parameters
        ----------
        qid: str
            The QID of the subclass to retrieve.
        
        Returns
        -------
        WikidataClass
            The subclass associated with the given QID.

    `get_superclass(self, qid: str) ‑> knowledge.public.wikidata.WikidataClass`
    :   Retrieves a superclass from the superclass cache.
        
        Parameters
        ----------
        qid: str
            The QID of the superclass to retrieve.
        
        Returns
        -------
        WikidataClass
            The superclass associated with the given QID.

    `get_wikidata_object(self, qid: str) ‑> knowledge.public.wikidata.WikidataThing`
    :   Retrieves a Wikidata object from the cache.
        
        Parameters
        ----------
        qid: str
            The QID of the Wikidata object to retrieve.
        
        Returns
        -------
        WikidataThing
            The Wikidata object associated with the given QID.

    `load_cache(self, cache_path: pathlib.Path) ‑> None`
    :   Loads the cache from a path.
        
        Parameters
        ----------
        cache_path: Path
            The path to the file from which the cache will be loaded.

    `number_of_cached_objects(self) ‑> int`
    :   Returns the number of cached objects.
        
        Returns
        -------
        int
            The number of objects in the cache.

    `number_of_cached_properties(self) ‑> int`
    :   Returns the number of cached properties.
        
        Returns
        -------
        int
            The number of properties in the cache.

    `number_of_cached_subclasses(self) ‑> int`
    :   Returns the number of cached subclasses.
        
        Returns
        -------
        int
            The number of subclasses in the cache.

    `number_of_cached_superclasses(self) ‑> int`
    :   Returns the number of cached superclasses.
        
        Returns
        -------
        int
            The number of superclasses in the cache.

    `property_in_cache(self, pid: str) ‑> bool`
    :   Checks if a property is in the cache.
        
        Parameters
        ----------
        pid: str
            The PID to check.
        
        Returns
        -------
        bool
            True if the PID is in the cache, False otherwise.

    `qid_in_cache(self, qid: str) ‑> bool`
    :   Checks if a QID is in the cache.
        
        Parameters
        ----------
        qid: str
            The QID to check.
        
        Returns
        -------
        bool
            True if the QID is in the cache, False otherwise.

    `save_cache(self, cache_path: pathlib.Path)`
    :   Saves the cache to a file.
        
        Parameters
        ----------
        cache_path: Path
            The path to the file where the cache will be saved.

    `subclass_in_cache(self, qid: str) ‑> bool`
    :   Checks if a subclass is in the cache.
        
        Parameters
        ----------
        qid: str
            The QID to check.
        
        Returns
        -------
        bool
            True if the QID is in the subclass cache, False otherwise.

    `superclass_in_cache(self, qid: str) ‑> bool`
    :   Checks if a superclass is in the cache.
        
        Parameters
        ----------
        qid: str
            The QID to check.
        
        Returns
        -------
        bool
            True if the QID is in the superclass cache, False otherwise.