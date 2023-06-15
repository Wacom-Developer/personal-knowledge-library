Module knowledge.utils.wikipedia
================================

Functions
---------

    
`get_wikipedia_summary(title: str, lang: str = 'en') ‑> str`
:   Extracting summary wikipedia URL.
    
    Parameters
    ----------
    title: str
        Title of the Wikipedia article
    lang: str
        Language code
    
    Returns
    -------
    result: dict[str, str]
        Summary dict with image and summary text

    
`get_wikipedia_summary_image(title: str, lang: str = 'en') ‑> dict[str, str]`
:   Extracting summary image and abstract for wikipedia URL.
    
    Parameters
    ----------
    title: str
        Title of the Wikipedia article
    lang: str
        Language code
    
    Returns
    -------
    result: dict[str, str]
        Summary dict with image and summary text

    
`get_wikipedia_summary_url(wiki_url: str, lang: str = 'en') ‑> dict[str, str]`
:   Extracting summary image and abstract for wikipedia URL.
    Parameters
    ----------
    wiki_url: str
        Wikipedia URL
    lang: str
        Language code
    
    Returns
    -------
    result: dict[str, str]
        Result dictionary.

Classes
-------

`ExtractionException(*args, **kwargs)`
:   Exception for extraction errors.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException