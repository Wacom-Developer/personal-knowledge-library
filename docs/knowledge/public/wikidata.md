Module knowledge.public.wikidata
================================

Functions
---------

    
`chunks(lst: list[str], chunk_size: int)`
:   Yield successive n-sized chunks from lst.Yield successive n-sized chunks from lst.
    Parameters
    ----------
    lst: list[str]
        Full length.
    chunk_size: int
        Chunk size.

    
`detect_cycle(super_class_qid: str, cycle_detector: list[tuple[str, str]])`
:   

Classes
-------

`Claim(pid: knowledge.public.wikidata.WikidataProperty, literal: list[dict[str, typing.Any]], qualifiers: list[dict[str, typing.Any]])`
:   Claim
    ------
    A Wikidata claim is a statement that describes a particular property-value relationship about an item in the
    Wikidata knowledge base. In Wikidata, an item represents a specific concept, such as a person, place, or
    organization, and a property describes a particular aspect of that concept, such as its name, date of birth,
    or location.
    
    A claim consists of three elements:
    
    - Subject: The item to which the statement applies
    - Predicate: The property that describes the statement
    - Object: The value of the property for the given item
    
    For example, a claim could be "Barack Obama (subject) has a birth-date (predicate) of August 4, 1961 (object)."
    Claims in Wikidata help to organize information and provide a structured way to represent knowledge that can
    be easily queried, analyzed, and visualized.

    ### Static methods

    `create_from_dict(claim) ‑> knowledge.public.wikidata.Claim`
    :   Create a claim from a dictionary.

    ### Instance variables

    `literals: list[dict[str, typing.Any]]`
    :   Literals. Objects of the statement.

    `pid: knowledge.public.wikidata.WikidataProperty`
    :   Property name. Predicate of the claim.

    `qualifiers: list[dict[str, typing.Any]]`
    :   Qualifiers.

`SiteLinks(source: str)`
:   SiteLinks
    ---------
    Sitelinks in Wikidata are links between items in Wikidata and pages on external websites, such as Wikipedia,
    Wikimedia Commons, and other Wikimedia projects. A sitelink connects a Wikidata item to a specific page on an
    external website that provides more information about the topic represented by the item.
    
    For example, a Wikidata item about a particular city might have sitelinks to the corresponding page on the English,
    French, and German Wikipedia sites. Each sitelink connects the Wikidata item to a specific page on the external
    website that provides more detailed information about the city.
    
    Sitelinks in Wikidata help to connect and integrate information across different languages and projects,
    making it easier to access and share knowledge on a wide range of topics. They also help to provide context and
    additional information about Wikidata items, improving the overall quality and usefulness of the knowledge base.
    
    Parameters
    ----------
    source: str
        Source of sitelinks.

    ### Static methods

    `create_from_dict(entity_dict: dict[str, typing.Any]) ‑> knowledge.public.wikidata.SiteLinks`
    :   Create a SiteLinks object from a dictionary.
        
        Parameters
        ----------
        entity_dict: dict[str, Any]
            dictionary containing the entity information.
        
        Returns
        -------
        instance: SiteLinks
            SiteLinks instance.

    ### Instance variables

    `source: str`
    :   Sitelinks source.

    `titles: dict[str, str]`
    :   Titles for the source.

    `urls: dict[str, str]`
    :   URLs for the source.

    `urls_languages: list[str]`
    :   List of all supported languages.

`WikiDataAPIClient()`
:   WikiDataAPIClient
    -----------------
    Utility class for the WikiData.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Static methods

    `retrieve_entities(qids: Union[list[str], set[str]]) ‑> list[knowledge.public.wikidata.WikidataThing]`
    :   Retrieve multiple Wikidata things.
        Parameters
        ----------
        qids: list[str]
            QIDs of the entities.
        
        Returns
        -------
        instances: list[WikidataThing]
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

    `search_term(search_term: str, language: str, url: str = 'https://www.wikidata.org/w/api.php') ‑> list[knowledge.public.wikidata.WikidataSearchResult]`
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
        search_results_dict: list[WikidataSearchResult]
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

    `superclasses(qid: str) ‑> Optional[knowledge.public.wikidata.WikidataClass]`
    :

`WikidataClass(qid: str, label: Optional[str] = None)`
:   WikidataClass
    ----------------
    In Wikidata, classes are used to group items together based on their common characteristics.
    Classes in Wikidata are represented as items themselves, and they are typically identified by the prefix "Q"
    followed by a unique number.
    
    There are several types of classes in Wikidata, including:
    
    - **Main Classes**: These are the most general classes in Wikidata, and they represent broad categories of items.
    Examples of main classes include "person" (Q215627), "physical location" (Q17334923), and "event" (occurrence).
    - **Subclasses**: These are more specific classes that are grouped under a main class.
    For example, "politician" (Q82955) is a subclass of "person" (Q215627), and "city" (Q515) is a subclass
    of "location" (Q17334923).
    - **Properties**: These are classes that represent specific attributes or characteristics of items. For example,
    "gender" (Q48277) is a property that can be used to describe the gender of a person.
    - **Instances**: These are individual items that belong to a class. For example, Barack Obama (Q76) is an instance
    of the "person" (Q215627) class.
    - **Metaclasses**: These are classes that are used to group together other classes based on their properties or
    characteristics. For example, the "monotypic taxon" (Q310890) class groups together classes that represent
    individual species of organisms.
    
    Overall, classes in Wikidata are a tool for organizing and categorizing information in a structured and consistent
    way, which makes it easier to search and analyze data across a wide range of topics and domains.
    
    Parameters
    ----------
    qid: str
        Class QID.

    ### Static methods

    `create_from_dict(class_dict: dict[str, typing.Any]) ‑> knowledge.public.wikidata.WikidataClass`
    :

    ### Instance variables

    `label: str`
    :   Label with lazy loading mechanism.

    `qid`
    :   Property id.

    `superclasses: list['WikidataClass']`
    :

`WikidataProperty(pid: str, label: Optional[str] = None)`
:   WikidataProperty
    ----------------
    Property id and its label from wikidata.
    
    Parameters
    ----------
    pid: str
        Property ID.

    ### Static methods

    `create_from_dict(prop_dict: dict[str, typing.Any]) ‑> knowledge.public.wikidata.WikidataProperty`
    :

    ### Instance variables

    `label: str`
    :   Label with lazy loading mechanism.

    `label_cached: str`
    :   Label with cached value.

    `pid`
    :   Property id.

`WikidataSearchResult(qid: str, label: knowledge.base.entity.Label, description: Optional[knowledge.base.entity.Description], repository: str, aliases: list[str])`
:   WikidataSearchResult
    --------------------
    Search result from wikidata.

    ### Static methods

    `from_dict(search_result: dict[str, typing.Any]) ‑> knowledge.public.wikidata.WikidataSearchResult`
    :

    ### Instance variables

    `description: Optional[knowledge.base.entity.Description]`
    :

    `label: knowledge.base.entity.Label`
    :

    `qid: str`
    :

    `repository: str`
    :

`WikidataThing(revision: str, qid: str, modified: datetime.datetime, label: Optional[dict[str, knowledge.base.entity.Label]] = None, aliases: Optional[dict[str, list[knowledge.base.entity.Label]]] = None, description: Optional[dict[str, knowledge.base.entity.Description]] = None)`
:   WikidataEntity
    -----------
    Generic entity within wikidata.
    
    Each entity is derived from this object, thus all entity shares:
    - **qid**: A unique resource identity to identify the entity and reference it in relations
    - **label**: Human understandable label
    - **description**: Description of entity
    
    Parameters
    ----------
    label: list[Label]
        List of labels
    description: list[Description] (optional)
        List of descriptions
    qid: str
         QID for entity. For new entities the URI is None, as the knowledge graph backend assigns this.

    ### Static methods

    `create_from_dict(entity_dict: dict[str, typing.Any]) ‑> knowledge.public.wikidata.WikidataThing`
    :   Create WikidataThing from dict.
        
        Parameters
        ----------
        entity_dict: dict[str, Any]
            dictionary with WikidataThing information.
        
        Returns
        -------
        thing: WikidataThing
            Instance of WikidataThing

    `from_wikidata(entity_dict: dict[str, typing.Any], supported_languages: Optional[list[str]] = None) ‑> knowledge.public.wikidata.WikidataThing`
    :   Create WikidataThing from Wikidata JSON response.
        Parameters
        ----------
        entity_dict: dict[str, Any]
            dictionary with WikidataThing information.
        supported_languages: Optional[list[str]]
            List of supported languages. If None, all languages are supported.
        
        Returns
        -------
        thing: WikidataThing
            Instance of WikidataThing.

    ### Instance variables

    `alias_languages: list[str]`
    :   All available languages for a aliaes.

    `aliases: dict[str, list[knowledge.base.entity.Label]]`
    :   Alternative labels of the concept.

    `claim_properties: list[knowledge.public.wikidata.WikidataProperty]`
    :

    `claims: dict[str, knowledge.public.wikidata.Claim]`
    :

    `claims_dict: dict[str, knowledge.public.wikidata.Claim]`
    :

    `description: dict[str, knowledge.base.entity.Description]`
    :   Description of the thing (optional).

    `description_languages: list[str]`
    :

    `instance_of: list[knowledge.public.wikidata.WikidataClass]`
    :

    `label: dict[str, knowledge.base.entity.Label]`
    :   Labels of the entity.

    `label_languages: list[str]`
    :   All available languages for a labels.

    `modified: datetime.datetime`
    :   Modification date of entity.

    `ontology_types: list[str]`
    :   Ontology types of the entity.

    `qid: str`
    :   QID for entity.

    `revision: str`
    :   Revision version of entity.

    `sitelinks: dict[str, knowledge.public.wikidata.SiteLinks]`
    :   Different sitelinks assigned to entity.

    ### Methods

    `add_alias(self, alias: str, language_code: str)`
    :   Adding an alias for entity.
        
        Parameters
        ----------
        alias: str
            Alias
        language_code: str
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `add_claim(self, pid: str, claim: knowledge.public.wikidata.Claim)`
    :   Adding a claim.
        
        Parameters
        ----------
        pid: str
            Property ID.
        claim: Claim
            Wikidata claim

    `add_description(self, description: str, language_code: str)`
    :   Adding a description for entity.
        
        Parameters
        ----------
        description: str
            Description
        language_code: str
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `add_label(self, label: str, language_code: str)`
    :   Adding a label for entity.
        
        Parameters
        ----------
        label: str
            Label
        language_code: str
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `alias_lang(self, language_code: knowledge.base.entity.LanguageCode) ‑> list[knowledge.base.entity.Label]`
    :   Get alias for language_code code.
        
        Parameters
        ----------
        language_code: LanguageCode
            Requested language_code code
        Returns
        -------
        aliases: list[Label]
            Returns a list of aliases for a specific language code

    `description_lang(self, language_code: str) ‑> Optional[knowledge.base.entity.Description]`
    :   Get description for entity.
        
        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        Returns
        -------
        label: LocalizedContent
            Returns the  label for a specific language_code code

    `image(self, dpi: int = 500) ‑> Optional[str]`
    :   Generate URL for image from Wikimedia.
        
        Parameters
        ----------
        dpi: int
            DPI value. Range: [50-1000]
        
        Returns
        -------
        wikimedia_url: str
            URL for Wikimedia

    `label_lang(self, language_code: str) ‑> Optional[knowledge.base.entity.Label]`
    :   Get label for language_code code.
        
        Parameters
        ----------
        language_code: LanguageCode
            Requested language_code code
        Returns
        -------
        label: Optional[Label]
            Returns the label for a specific language code