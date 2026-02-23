Module knowledge.public.helper
==============================

Functions
---------

`__waiting_multi_request__(entity_ids: List[str], base_url: str = 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids=', timeout: int = 60, max_retries: int = 3, backoff_factor: float = 0.1) ‑> List[Dict[str, Any]]`
:   Sena a request to retrieve multiple entities with retry policy.
    
    Parameters
    ----------
    entity_ids: List[str]
        Entity QIDs
    base_url: Base URL
        The base URL
    timeout:  int
        Timeout in seconds
    max_retries: int
        Maximum number of retries
    backoff_factor: float
        Backoff factor for retries.
    Returns
    -------
    result_dict: Dict[str, Any]
        Result dict
    Raises
    ------
    ValueError - Empty list or to many entities

`__waiting_request__(entity_id: str, base_url: str = 'https://www.wikidata.org/wiki/Special:EntityData', timeout: int = 60, max_retries: int = 3, backoff_factor: float = 0.1) ‑> Dict[str, Any]`
:   Sena a request with retry policy.
    
    Parameters
    ----------
    entity_id: str
        Entity QID
    base_url: Base URL
        The base URL
    timeout:  int
        Timeout in seconds
    max_retries: int
        Maximum number of retries
    backoff_factor: float
        Backoff factor for retries.
    
    Returns
    -------
    result_dict: Dict[str, Any]
        Result dict

`image_url(img: str, dpi: int = 500)`
:   Helper to generate image URL for Wikipedia.
    
    Parameters
    ----------
    img: str
        Name of image
    dpi: int
        DPI of the generated URL
    Returns
    -------
    wikimedia_url: str
        URL of wikimedia

`parse_date(date_string: str) ‑> datetime.datetime | None`
:   Parse date string to datetime object.
    Parameters
    ----------
    date_string: str
        Date string
    
    Returns
    -------
    parsed_date: datetime
        Parsed date

`user_agent() ‑> str`
:   User agent.

`wikidate(param: Dict[str, Any]) ‑> Dict[str, Any]`
:   Parse and extract wikidata structure.
    Parameters
    ----------
    param: Dict[str, Any]
        Entities wikidata
    
    Returns
    -------
    result: Dict[str, Any]
        Dict with pretty print of date

Classes
-------

`Precision(*args, **kwds)`
:   Precision enum for date.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `BILLION_YEARS`
    :   The type of the None singleton.

    `CENTURY`
    :   The type of the None singleton.

    `DAY`
    :   The type of the None singleton.

    `DECADE`
    :   The type of the None singleton.

    `HUNDREDS_THOUSAND_YEARS`
    :   The type of the None singleton.

    `MILLENIUM`
    :   The type of the None singleton.

    `MILLION_YEARS`
    :   The type of the None singleton.

    `MONTH`
    :   The type of the None singleton.

    `TEN_THOUSAND_YEARS`
    :   The type of the None singleton.

    `YEAR`
    :   The type of the None singleton.

`WikiDataAPIException(*args, **kwargs)`
:   WikiDataAPIException
    --------------------
    Exception thrown when accessing WikiData fails.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException