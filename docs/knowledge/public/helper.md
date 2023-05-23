Module knowledge.public.helper
==============================

Functions
---------

    
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

    
`wikidate(param: Dict[str, Any]) ‑> Dict[str, Any]`
:   Parse and extract wikidata structure.
    Parameters
    ----------
    param: Dict[str, Any]
        Entity wikidata
    
    Returns
    -------
    result: Dict[str, Any]
        Dict with pretty print of date

Classes
-------

`Precision(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Precision enum for date.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `BILLION_YEARS`
    :

    `CENTURY`
    :

    `DAY`
    :

    `DECADE`
    :

    `HUNDREDS_THOUSAND_YEARS`
    :

    `MILLENIUM`
    :

    `MILLION_YEARS`
    :

    `MONTH`
    :

    `TEN_THOUSAND_YEARS`
    :

    `YEAR`
    :

`WikiDataAPIException(*args, **kwargs)`
:   WikiDataAPIException
    --------------------
    Exception thrown when accessing WikiData fails.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException