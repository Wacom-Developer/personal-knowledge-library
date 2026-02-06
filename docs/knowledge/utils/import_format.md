Module knowledge.utils.import_format
====================================

Functions
---------

`append_import_format(file_path: pathlib.Path, entity: knowledge.base.ontology.ThingObject) ‑> None`
:   Append to the import format file.
    Parameters
    ----------
    file_path: Path
        The path to the file.
    entity: ThingObject
        The entity to append.

`is_http_url(url: str) ‑> bool`
:   Check if a string is an HTTP(S) URL.
    Parameters
    ----------
    url: str
        The URL to check.
    
    Returns
    -------
    bool
        True if the URL is HTTP(S), False otherwise.

`is_local_url(url: str) ‑> bool`
:   Check if a string is a local file path or relative URL.
    Parameters
    ----------
    url: str
        The URL to check.
    
    Returns
    -------
    bool
        True if the URL is a local file path or relative URL, False otherwise.

`iterate_large_import_format(file_path: pathlib.Path) ‑> Iterable[knowledge.base.ontology.ThingObject]`
:   Iterates over a gzip‑compressed file containing ThingObject JSON lines, yielding parsed ThingObject instances.
    
    Parameters
    ----------
    file_path
        Path to the gzip‑compressed input file.
    
    Yields
    ------
    ThingObject
        Parsed ThingObject instance for each line in the input file.
    
    Returns
    -------
    Iterable[ThingObject]
        An iterator yielding ThingObject instances.
    
    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file format is not supported.

`load_import_format(file_path: pathlib.Path) ‑> List[knowledge.base.ontology.ThingObject]`
:   Load the import format file.
    Parameters
    ----------
    file_path:  Path
        The path to the file.
    
    Returns
    -------
    entity_list: List[ThingObject]
        The list of entities.
    
    Raises
    ------
    FileNotFoundError
        If the file does not exist or is not a file.

`save_import_format(file_path: pathlib.Path, entities: List[knowledge.base.ontology.ThingObject], save_groups: bool = True, generate_missing_ref_ids: bool = True) ‑> None`
:   Save the import format file.
    Parameters
    ----------
    file_path: Path
        The path to the file.
    entities: List[ThingObject]
        The list of entities.
    save_groups: bool
        Whether to save groups or not.
    generate_missing_ref_ids: bool
        Whether to generate missing reference IDs or not.