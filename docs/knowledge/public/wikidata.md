Module knowledge.public.wikidata
================================

Functions
---------

    
`wikidate(param: Dict[str, Any]) ‑> dict`
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

    `YEAR`
    :

`WikiDataAPIClient()`
:   WikiData API client.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Class variables

    `ACTIVATION_RELATIONS`
    :

    `PROPERTY_OFFICIAL_WEBSITE: str`
    :

    `PROPERTY_PERSON_FIRSTNAME: str`
    :

    `PROPERTY_PERSON_LASTNAME: str`
    :

    ### Static methods

    `image_url(img: str)`
    :

    `property(pid: str, language: str = 'en')`
    :   Extract property.
        
        :param pid: property id
        :param language: language_code code for property name
        :return: property nam

    `subclasses(qid: str) ‑> list`
    :   Check for subclasses.
        
        :param qid: QID of entity
        :return: list of subclasses QIDs

    `wikipedia_url(wikidata_id: str, lang: str = 'en')`
    :

    ### Methods

    `activations(self, uris: list, language: str = 'en') ‑> tuple`
    :   Activations of URIs
        :param uris: list of URIs
        :param language: language_code of entity
        :return: list of entities, list of relations

    `entities_rel(self, qids: list, language: str = 'en') ‑> tuple`
    :   Return relations and entities for qids.
        
        :param qids: list of entities in Wikidata
        :param language: language_code the content
        :return: entities, relations

    `entity(self, qid: str, language: str = 'en', pull_wiki_content: bool = False) ‑> dict`
    :   Get entity information from public including relations
        
        :param qid: QID representing the entity in the public knowledge graph
        :param language: language_code for text
        :param pull_wiki_content: pulling extended description and summary
        :return: dict with relevant information

    `entity_lang(self, qid: ItemId, languages: List[LanguageCode] = None, pull_wiki_content: bool = False) ‑> dict`
    :   Get entity information from public including relations
        
        :param qid: str -
         QID representing the entity in the public knowledge graph
        :param languages: List[str] -
            List of languages for text
        :param pull_wiki_content: pulling extended description and summary
        :return: dict with relevant information

    `entity_rels(self, qid: str, language: str = 'en', pull_wiki_content: bool = False) ‑> Tuple[dict, dict]`
    :   Get entity information from public including relations
        
        :param qid: QID representing the entity in the public knowledge graph
        :param language: language_code for text
        :param pull_wiki_content: pulling extended description and summary
        :return: dict with relevant information

    `entity_rels_lang(self, qid: str, languages: List[LanguageCode] = None, pull_wiki_content: bool = False, default_language: str = 'en') ‑> tuple`
    :   Get entity information from public including relations.
        
        :param qid: str -
            QID representing the entity in the public knowledge graph
        :param languages: List[str] -
            List of languages for text
        :param pull_wiki_content: bool -
            Pulling extended description and summary
        :param default_language: str -
            Default language_code
        :return: dict with relevant information

    `references(self, qid: str, language: str = 'en')`
    :

`WikiDataAPIException(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException