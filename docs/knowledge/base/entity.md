Module knowledge.base.entity
============================

Classes
-------

`Description(description: str, language_code: knowledge.base.entity.LanguageCode = 'en_US')`
:   Description
    -----------
    Description that is multi-lingual.
    
    Parameters
    ----------
    description: str
        Description value
    language_code: LanguageCode (default:= 'en_US')
        Language code of content

    ### Ancestors (in MRO)

    * knowledge.base.entity.LocalizedContent
    * abc.ABC

    ### Static methods

    `create_from_dict(dict_description: Dict[str, Any], tag_name: str = 'description', locale_name: str = 'locale') ‑> knowledge.base.entity.Description`
    :   Create a description from a dictionary.
        
        Parameters
        ----------
        dict_description: Dict[str, Any]
            Dictionary containing the description information.
        tag_name: str
            Tag name of the content.
        locale_name:
            Tag name of the language code.
        
        Returns
        -------
        instance: Description
            Description instance.

    `create_from_list(param: List[Dict[str, Any]]) ‑> List[knowledge.base.entity.Description]`
    :   Create a list of descriptions from a list of dictionaries.
        
        Parameters
        ----------
        param: List[Dict[str, Any]]
            List of dictionaries containing the description information.
        
        Returns
        -------
        instance: List[Description]
            List of description instances.

`EntityStatus(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Entity Status
    -------------
    Status of the entity synchronization (client and knowledge graph).

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CREATED`
    :   Entity has been created and not yet update.

    `SYNCED`
    :   State of entity is in sync with knowledge graph.

    `UNKNOWN`
    :   Unknown status.

    `UPDATED`
    :   Entity has been updated by the client and must be synced.

`KnowledgeException(*args, **kwargs)`
:   Knowledge exception.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`Label(content: str, language_code: knowledge.base.entity.LanguageCode = 'en_US', main: bool = False)`
:   Label
    -----
    Label that is multi-lingual.
    
    Parameters
    ----------
    content: str
        Content value
    language_code: LanguageCode (default:= 'en_US')
        Language code of content
    main: bool (default:=False)
        Main content

    ### Ancestors (in MRO)

    * knowledge.base.entity.LocalizedContent
    * abc.ABC

    ### Static methods

    `create_from_dict(dict_label: Dict[str, Any], tag_name: str = 'value', locale_name: str = 'locale') ‑> knowledge.base.entity.Label`
    :   Create a label from a dictionary.
        Parameters
        ----------
        dict_label: Dict[str, Any]
            Dictionary containing the label information.
        tag_name: str
            Tag name of the content.
        locale_name: str
            Tag name of the language code.
        
        Returns
        -------
        instance: Label
            Label instance.

    `create_from_list(param: List[dict]) ‑> List[knowledge.base.entity.LocalizedContent]`
    :   Create a list of labels from a list of dictionaries.
        
        Parameters
        ----------
        param: List[dict]
            List of dictionaries containing the label information.
        
        Returns
        -------
        instance: List[Label]
            List of label instances.

    ### Instance variables

    `main: bool`
    :   Flag if the content is the  main content or an alias.

`LocalizedContent(content: str, language_code: knowledge.base.entity.LanguageCode = 'en_US')`
:   Localized content
    -----------------
    Content that is multi-lingual.
    
    Parameters
    ----------
    content: str
        Content value
    language_code: LanguageCode (default:= 'en_US')
        ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.base.entity.Description
    * knowledge.base.entity.Label
    * knowledge.base.ontology.Comment
    * knowledge.base.ontology.OntologyLabel

    ### Instance variables

    `content: str`
    :   String representation of the content.

    `language_code: knowledge.base.entity.LanguageCode`
    :   Language code of the content.

`ServiceException(*args, **kwargs)`
:   Service exception.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException