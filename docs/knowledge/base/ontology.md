Module knowledge.base.ontology
==============================

Classes
-------

`Comment(text: str, language_code: knowledge.base.language.LanguageCode = 'en')`
:   Comment
    -------
    Comment that is multi-lingual.
    
    Parameters
    ----------
    text: str
        Text value
    language_code: LanguageCode (default:= 'en')
        Language code of content

    ### Ancestors (in MRO)

    * knowledge.base.entity.LocalizedContent
    * abc.ABC

    ### Static methods

    `create_from_dict(dict_description: Dict[str, Any]) ‑> knowledge.base.ontology.Comment`
    :   Create a comment from a dictionary.
        Parameters
        ----------
        dict_description: Dict[str, Any]
            Dictionary containing the comment
        
        Returns
        -------
        instance: Comment
            Instance of comment

    `create_from_list(param: List[Dict[str, Any]]) ‑> List[knowledge.base.ontology.Comment]`
    :   Create a list of comments from a list of dictionaries.
        Parameters
        ----------
        param: List[Dict[str, Any]]
            List of dictionaries containing the comments
        
        Returns
        -------
        instances: List[Comment]
            List of instances of comments

    ### Methods

    `as_dict(self) ‑> Dict[str, Any]`
    :   Return a dictionary representation of the object.
        
        Returns
        -------
        dict
            A mapping where the key ``COMMENT_TAG`` maps to the object's
            ``content`` attribute and the key ``LOCALE_TAG`` maps to the
            object's ``language_code`` attribute.

`DataProperty(content: Any, property_ref: knowledge.base.ontology.OntologyPropertyReference, language_code: knowledge.base.language.LocaleCode = 'en_US', data_type: knowledge.base.ontology.DataPropertyType | None = None)`
:   DataProperty
    ------------
    Data property for entities.
    
    Parameter
    ---------
    content: Any
        Content
    literal_type: LiteralProperty
        OntologyPropertyReference type
    language_code: str
        Language code
    data_type: Optional[DataPropertyType] (default: None)
        Data type

    ### Ancestors (in MRO)

    * knowledge.base.ontology.EntityProperty
    * abc.ABC

    ### Static methods

    `create_from_dict(data_property_struct: Dict[str, Any]) ‑> knowledge.base.ontology.DataProperty`
    :   Create a data property from a dictionary.
        
        Parameters
        ----------
        data_property_struct: dict
            Dictionary containing data property information.
        
        Returns
        -------
        instance: DataProperty
            Data property instance.

    `create_from_list(param: List[Dict[str, Any]]) ‑> List[knowledge.base.ontology.DataProperty]`
    :   Create a data property list from a dictionary list.
        
        Parameters
        ----------
        param: List[Dict[str, Any]]
            List of dictionaries containing data property information.
        
        Returns
        -------
        instances: List[DataProperty]
            List of data property instances.

    ### Instance variables

    `data_property_type: knowledge.base.ontology.OntologyPropertyReference`
    :   Ontology type.

    `data_type: knowledge.base.ontology.DataPropertyType | None`
    :   Data type (optional).

    `language_code: knowledge.base.language.LocaleCode`
    :   Language code of the content.

    `value: Any`
    :   Content of the data property.

    ### Methods

    `as_dict(self) ‑> Dict[str, Any]`
    :   Returns a dictionary representing the object's content, locale, and data type.
        
        Parameters
        ----------
        self : object
            Instance of the class.
        
        Returns
        -------
        A mapping of the following keys:
            CONTENT_TAG, LOCALE_TAG, DATA_PROPERTY_TAG, and DATA_TYPE_TAG.
        The values correspond to the object's value, language_code,
        data_property_type.iri, and data_type.value (or None if data_type is None).

`DataPropertyType(*args, **kwds)`
:   DataPropertyType.
    -----------------
    Data types that are used by Datatype properties.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `ANY_URI`
    :   Absolute or relative URIs and IRIs

    `BASE64_BINARY`
    :   Base64-encoded binary data

    `BOOLEAN`
    :   boolean: true, false

    `BYTES`
    :   -128…+127 (8 bit)

    `DATE`
    :   Dates (yyyy-mm-dd) with or without timezone

    `DATE_TIME`
    :   Date and time with or without timezone

    `DATE_TIMESTAMP`
    :   Date and time with required timezone

    `DAYTIME_DURATION`
    :   Duration of time (days, hours, minutes, seconds only)

    `DECIMAL`
    :   Arbitrary-precision decimal numbers

    `DOUBLE`
    :   64-bit floating point numbers incl. ±Inf, ±0, NaN

    `DURATION`
    :   Duration of time

    `FLOAT`
    :   32-bit floating point numbers incl. ±Inf, ±0, NaN

    `G_DAY`
    :   Gregorian calendar day of the month

    `G_MONTH`
    :   Gregorian calendar month

    `G_MONTH_DAY`
    :   Gregorian calendar month and day

    `G_YEAR`
    :   Gregorian calendar year

    `G_YEAR_MONTH`
    :   Gregorian calendar year and month

    `HEX_BINARY`
    :   Hex-encoded binary data

    `INT`
    :   -2147483648…+2147483647 (32 bit)

    `INTEGER`
    :   Arbitrary-size integer numbers

    `LANGUAGE`
    :   Language tags per http://tools.ietf.org/html/bcp47

    `LONG`
    :   -9223372036854775808…+9223372036854775807 (64 bit)

    `NAME`
    :   XML Names

    `NC_NAME`
    :   XML NCNames

    `NEGATIVE_INTEGER`
    :   Integer numbers ≤ 0

    `NM_TOKEN`
    :   XML NMTOKENs

    `NON_NEGATIVE_INTEGER`
    :   Integer numbers ≥ 0

    `NON_POSITIVE_INTEGER`
    :   Integer numbers ≤ 0

    `NORMALIZED`
    :   Whitespace-normalized strings

    `POSITIVE_INTEGER`
    :   Integer numbers > 0

    `SHORT`
    :   -32768… + 32767 (16 bit)

    `STRING`
    :   Character strings (but not all Unicode character strings)

    `TIME`
    :   Times (hh:mm:ss.sss…) with or without timezone

    `TOKEN`
    :   Tokenized strings

    `UNSIGNED_BYTE`
    :   0 … 255 (8 bit)

    `UNSIGNED_INT`
    :   0 … 4294967295 (32 bit)

    `UNSIGNED_LONG`
    :   0 … 18446744073709551615 (64 bit)

    `UNSIGNED_SHORT`
    :   0 … 65535 (16 bit)

    `YEAR_MONTH_DURATION`
    :   Duration of time (months and years only)

`InflectionSetting(concept: str, inflection: str, case_sensitive: bool)`
:   Inflection settings
    --------------------
    
    Parameters
    ----------
    concept: str
        Concept class
    inflection: str
        Inflection setting
    case_sensitive: bool
        Entity labels of the class treated case-sensitive

    ### Static methods

    `from_dict(entity: Dict[str, Any]) ‑> knowledge.base.ontology.InflectionSetting`
    :   Create an inflection setting from the dictionary.
        Parameters
        ----------
        entity: Dict[str, Any]
            Entity dictionary
        
        Returns
        -------
        instance: InflectionSetting
            Inflection setting instance

    ### Instance variables

    `case_sensitive: bool`
    :   Are entity labels of the class treated as case-sensitive?

    `concept: knowledge.base.ontology.OntologyClassReference`
    :   Concept class.

    `inflection: str`
    :   Inflection setting

`ObjectProperty(relation: knowledge.base.ontology.OntologyPropertyReference, incoming: List[str | ForwardRef('ThingObject')] | None = None, outgoing: List[str | ForwardRef('ThingObject')] | None = None)`
:   Object Property
    ---------------
    ObjectProperty for entities.
    
    Parameter
    ---------
    relation: OntologyPropertyReference
        The OntologyPropertyReference type
    incoming: List[str] (default:= [])
        Incoming relations
    outgoing: List[str] (default:= [])
        Outgoing relations

    ### Ancestors (in MRO)

    * knowledge.base.ontology.EntityProperty
    * abc.ABC

    ### Static methods

    `create_from_dict(relation_struct: Dict[str, Any]) ‑> Tuple[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.ObjectProperty]`
    :   Create object property from a dictionary.
        
        Parameters
        ----------
        relation_struct: Dict[str, Any]
            Dictionary containing object property information.
        
        Returns
        -------
        relation_type: OntologyPropertyReference
            The OntologyPropertyReference type

    `create_from_list(param: List[Dict[str, Any]]) ‑> Dict[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.ObjectProperty]`
    :   Create an object property list from a dictionary list.
        Parameters
        ----------
        param: List[Dict[str, Any]]
            List of dictionaries containing object property information.
        
        Returns
        -------
        instances: Dict[OntologyPropertyReference, ObjectProperty]
            Dictionary of object property instances.

    ### Instance variables

    `incoming_relations: List[str | ThingObject]`
    :   Incoming relation

    `outgoing_relations: List[str | ThingObject]`
    :   Outgoing relation

    `relation: knowledge.base.ontology.OntologyPropertyReference`
    :   Reference from the ontology.

    ### Methods

    `as_dict(self) ‑> Dict[str, Any]`
    :   Creates a dictionary representation of the object's relationships.
        
        Returns
        -------
        dict
            A mapping with the keys ``RELATION_TAG``, ``INCOMING_TAG``, and
            ``OUTGOING_TAG``.  The value associated with ``RELATION_TAG`` is the
            IRI of the relation linked to the object.  ``INCOMING_TAG`` contains a
            list of identifiers (either the URI or the reference ID) of all
            objects that have incoming relations to this object.  ``OUTGOING_TAG``
            holds a list of identifiers of all objects that this object points to.

`OntologyClass(tenant_id: str, context: str, reference: knowledge.base.ontology.OntologyClassReference, subclass_of: knowledge.base.ontology.OntologyClassReference | None = None, icon: str | None = None, labels: List[knowledge.base.ontology.OntologyLabel] | None = None, comments: List[knowledge.base.ontology.Comment] | None = None)`
:   OntologyClass
    ----------------
    Concept for ontology.
    
    Parameters
    ----------
    tenant_id: str
        Tenant id for ontology
    context: str
        Context
    subclass_of: Optional[OntologyClassReference] (default: None)
        Subclass of ontology class.
    reference: OntologyClassReference
        Reference for ontology class
    icon: Optional[str] (default: None)
        Icon representing concept
    labels: Optional[List[OntologyLabel]] (default: None)
        List of labels
    comments: Optional[List[Comment]] (default: None)
        List of comments

    ### Ancestors (in MRO)

    * knowledge.base.ontology.OntologyObject
    * abc.ABC

    ### Static methods

    `from_dict(concept_dict: Dict[str, Any]) ‑> knowledge.base.ontology.OntologyClass`
    :   Create OntologyClass from a dictionary.
        
        Parameters
        ----------
        concept_dict: Dict[str, Any]
            Dictionary containing the concept data.
        
        Returns
        -------
        instance: OntologyClass
            Instance of OntologyClass object.

    `new() ‑> knowledge.base.ontology.OntologyClass`
    :   Create a new ontology class.
        
        Returns
        -------
        instance: OntologyClass
            New ontology class.

    ### Instance variables

    `reference: knowledge.base.ontology.OntologyClassReference`
    :   Reference of ontology class.

    `subclass_of: knowledge.base.ontology.OntologyClassReference | None`
    :   Superclass of the class.

`OntologyClassReference(scheme: str, context: str, class_name: str)`
:   Ontology class type
    -------------------
    Associated with an ontology class.
    
    Parameters
    ----------
    scheme: str
        Scheme or owner
    context: str
        Context of class
    class_name: str
        Class name

    ### Ancestors (in MRO)

    * knowledge.base.ontology.OntologyObjectReference
    * abc.ABC

    ### Static methods

    `parse(iri: str) ‑> knowledge.base.ontology.OntologyClassReference`
    :   Parse IRI to create an ontology class reference.
        
        Parameters
        ----------
        iri: str
            IRI of ontology class reference
        
        Returns
        -------
        instance: OntologyClassReference
            Instance of ontology class reference

    ### Instance variables

    `class_name: str`
    :   Class name.

`OntologyContext(cid: str, tenant_id: str, name: str, icon: str, labels: List[knowledge.base.ontology.OntologyLabel], comments: List[knowledge.base.ontology.Comment], date_added: datetime.datetime, date_modified: datetime.datetime, context: str, base_uri: str, version: int, orphaned: bool, concepts: List[str] | None = None, properties: List[str] | None = None)`
:   OntologyContext
    ----------------
    Ontology context representation.
    
    Parameters
    ----------
    cid: str
        Context id
    tenant_id: str
        Tenant id.
    name: str
        Name of the ontology context
    icon: str
        Icon or Base64 encoded
    labels: List[OntologyLabel]
        List of labels
    comments: List[Comment]
        List of comments
    context: str
        context name
    base_uri: str
        Base URI
    concepts: List[str]
        List of classes / concepts
    properties: List[str]
        List of properties (data and object properties)

    ### Ancestors (in MRO)

    * knowledge.base.ontology.OntologyObject
    * abc.ABC

    ### Static methods

    `from_dict(context_dict: Dict[str, Any]) ‑> knowledge.base.ontology.OntologyContext`
    :   Create OntologyContext from a dictionary.
        
        Parameters
        ----------
        context_dict: Dict[str, Any]
            Dictionary containing the context data.
        
        Returns
        -------
        instance: OntologyContext
            Instance of OntologyContext object.

    ### Instance variables

    `base_uri: str`
    :   Base URI.

    `concepts: List[str]`
    :   List of concepts.

    `date_added: datetime.datetime`
    :   Date added.

    `date_modified: datetime.datetime`
    :   Date modified.

    `id: str`
    :   Context id.

    `orphaned: bool`
    :   Orphaned.

    `properties: List[str]`
    :   List of properties.

    `version: int`
    :   Version.

`OntologyLabel(content: str, language_code: knowledge.base.language.LanguageCode = 'en', main: bool = False)`
:   Ontology Label
    --------------
    Label that is multilingual.
    
    Parameters
    ----------
    content: str
        Content value
    language_code: LanguageCode (default:= 'en')
        Language code of content
    main: bool (default:=False)
        Main content

    ### Ancestors (in MRO)

    * knowledge.base.entity.LocalizedContent
    * abc.ABC

    ### Static methods

    `create_from_dict(dict_label: Dict[str, Any], tag_name: str = 'value', locale_name: str = 'locale') ‑> knowledge.base.ontology.OntologyLabel`
    :   Create a label from a dictionary.
        
        Parameters
        ----------
        dict_label: Dict[str, Any]
            Dictionary with the label information
        tag_name: str
            Tag name of the content
        locale_name: str
            Tag name of the language code
        
        Returns
        -------
        instance: OntologyLabel
            Instance of the label

    `create_from_list(param: List[Dict[str, Any]]) ‑> List[knowledge.base.ontology.OntologyLabel]`
    :   Create a list of labels from a list of dictionaries.
        Parameters
        ----------
        param: List[Dict[str, Any]]
            List of dictionaries with the label information
        
        Returns
        -------
        instances: List[OntologyLabel]
            List of label instances

    ### Instance variables

    `main: bool`
    :   Flag if the content is the main content or an alias.

    ### Methods

    `as_dict(self) ‑> Dict[str, Any]`
    :   Returns a dictionary mapping tag constant to the object's content, language code, and main status.
        
        Returns
        -------
        dict
            A mapping with keys:
            CONTENT_TAG : str
                The content of the object.
            LOCALE_TAG : str
                The language code.
            IS_MAIN_TAG : bool
                Indicates if this is the main entry.
        
        Notes
        -----
        This method does not expose any private or protected attributes.

`OntologyProperty(kind: knowledge.base.ontology.PropertyType, tenant_id: str, context: str, name: knowledge.base.ontology.OntologyPropertyReference, icon: str | None = None, property_domain: List[knowledge.base.ontology.OntologyClassReference] | None = None, property_range: List[knowledge.base.ontology.OntologyClassReference | knowledge.base.ontology.DataPropertyType] | None = None, labels: List[knowledge.base.ontology.OntologyLabel] | None = None, comments: List[knowledge.base.ontology.Comment] | None = None, sub_property_of: knowledge.base.ontology.OntologyPropertyReference | None = None, inverse_property_of: knowledge.base.ontology.OntologyPropertyReference | None = None)`
:   Ontology Property
     -----------------
     Property ontology object.
    
     Parameters
     ----------
     kind: PropertyType
         Kind of relation
     tenant_id: str
         Tenant id
     context: str
         Context
     name: OntologyPropertyReference
         Name of property object
     icon: Optional[str] [default: = None]
         Icon describing the property
     property_domain: Optional[List[OntologyClassReference]] [default: = None]
         Domain for the property
     property_range: Optional[List[Union[OntologyClassReference, DataPropertyType]]] [default: = None]
         Range for the property
     labels: Optional[List[OntologyLabel]] (default: = None)
         List of labels (localized)
     comments: Optional[List[Comment]] (default: = None)
         List of comments
     sub_property_of: Optional[OntologyPropertyReference] (default: = None)
         Sub property of.
    inverse_property_of: Optional[OntologyPropertyReference] (default: = None)
         Inverse property

    ### Ancestors (in MRO)

    * knowledge.base.ontology.OntologyObject
    * abc.ABC

    ### Static methods

    `from_dict(property_dict: Dict[str, Any]) ‑> knowledge.base.ontology.OntologyProperty`
    :   Create ontology property from a dictionary.
        Parameters
        ----------
        property_dict: Dict[str, Any]
            Dictionary containing property information.
        
        Returns
        -------
        instance: OntologyProperty
            Ontology property instance.

    `new(kind: knowledge.base.ontology.PropertyType) ‑> knowledge.base.ontology.OntologyProperty`
    :   Create a new ontology property.
        Parameters
        ----------
        kind: PropertyType
            Kind of property.
        
        Returns
        -------
        instance: OntologyProperty
            New ontology property.

    ### Instance variables

    `domains: List[knowledge.base.ontology.OntologyClassReference]`
    :   Domain of the property.

    `inverse_property_of: knowledge.base.ontology.OntologyPropertyReference | None`
    :   Reference to the inverse property

    `is_data_property: bool`
    :   Check if a property is a data property.
        
        Returns
        -------
        is_data_property: bool
            True if a property is a data property, False otherwise.

    `kind: knowledge.base.ontology.PropertyType`
    :   Kind of the property.

    `ranges: List[knowledge.base.ontology.OntologyClassReference | knowledge.base.ontology.DataPropertyType]`
    :   Ranges of the property.

    `reference: knowledge.base.ontology.OntologyPropertyReference`
    :   Reference to property

    `subproperty_of: knowledge.base.ontology.OntologyPropertyReference | None`
    :   Reference to the super property

`OntologyPropertyReference(scheme: str, context: str, property_name: str)`
:   Property reference
    ------------------
    Associated with an ontology property.
    
    Parameters
    ----------
    scheme: str
        Scheme or owner
    context: str
        Context of class
    property_name: str
        Property name

    ### Ancestors (in MRO)

    * knowledge.base.ontology.OntologyObjectReference
    * abc.ABC

    ### Static methods

    `parse(iri: str) ‑> knowledge.base.ontology.OntologyPropertyReference`
    :   Parses an IRI into an OntologyPropertyReference.
        
        Parameters
        ----------
        iri: str
            IRI to parse
        
        Returns
        -------
        instance: OntologyPropertyReference
            Instance of OntologyPropertyReference

    ### Instance variables

    `property_name: str`
    :   Property name.

`PropertyType(*args, **kwds)`
:   PropertyType
    -----------
    Within the ontology two different property types are defined. A data- and an object property.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `DATA_PROPERTY`
    :   The type of the None singleton.

    `OBJECT_PROPERTY`
    :   The type of the None singleton.

`ThingEncoder(*, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, default=None)`
:   Thing encoder
    -------------
    Encoder for ThingObject, Label and Description objects.
    
    Constructor for JSONEncoder, with sensible defaults.
    
    If skipkeys is false, then it is a TypeError to attempt
    encoding of keys that are not str, int, float, bool or None.
    If skipkeys is True, such items are simply skipped.
    
    If ensure_ascii is true, the output is guaranteed to be str
    objects with all incoming non-ASCII characters escaped.  If
    ensure_ascii is false, the output can contain non-ASCII characters.
    
    If check_circular is true, then lists, dicts, and custom encoded
    objects will be checked for circular references during encoding to
    prevent an infinite recursion (which would cause an RecursionError).
    Otherwise, no such check takes place.
    
    If allow_nan is true, then NaN, Infinity, and -Infinity will be
    encoded as such.  This behavior is not JSON specification compliant,
    but is consistent with most JavaScript based encoders and decoders.
    Otherwise, it will be a ValueError to encode such floats.
    
    If sort_keys is true, then the output of dictionaries will be
    sorted by key; this is useful for regression tests to ensure
    that JSON serializations can be compared on a day-to-day basis.
    
    If indent is a non-negative integer, then JSON array
    elements and object members will be pretty-printed with that
    indent level.  An indent level of 0 will only insert newlines.
    None is the most compact representation.
    
    If specified, separators should be an (item_separator, key_separator)
    tuple.  The default is (', ', ': ') if *indent* is ``None`` and
    (',', ': ') otherwise.  To get the most compact JSON representation,
    you should specify (',', ':') to eliminate whitespace.
    
    If specified, default is a function that gets called for objects
    that can't otherwise be serialized.  It should return a JSON encodable
    version of the object or raise a ``TypeError``.

    ### Ancestors (in MRO)

    * json.encoder.JSONEncoder

    ### Methods

    `default(self, o: Any) ‑> Any`
    :   Implement this method in a subclass such that it returns
        a serializable object for ``o``, or calls the base implementation
        (to raise a ``TypeError``).
        
        For example, to support arbitrary iterators, you could
        implement default like this::
        
            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                # Let the base class default method raise the TypeError
                return super().default(o)

`ThingObject(label: List[knowledge.base.entity.Label] | None = None, concept_type: knowledge.base.ontology.OntologyClassReference = wacom:core#Thing, description: List[knowledge.base.entity.Description] | None = None, uri: str | None = None, icon: str | None = None, tenant_rights: knowledge.base.access.TenantAccessRight = [], owner: bool = True, use_for_nel: bool = True, use_vector_index: bool = False, use_vector_index_document: bool = False, use_full_text_index: bool = True)`
:   ThingObject
    -----------
    Generic entity within the knowledge graph.
    
    Each entity is derived from this object, thus all entities share:
    - **uri**: A unique resource identity to identify the entity and reference it in relations
    - **label**: Human understandable label
    - **icon**: Visual representation of the entity
    - **description**: Description of entity
    - **concept_type**: Type of the concept
    - **concept_type_info**: Information on the concept type
    - **visibility**: Visibility of the entity
    - **use_for_nel**: Use the entity for named entity linking
    
    Parameters
    ----------
    label: Optional[List[Label]] (default:= None)
        List of labels
    icon: str (default:= None)
        Icon
    description: List[Description] (default:= [])
        List of descriptions
    concept_type: OntologyClassReference (default:= None)
        Type of the concept
    uri: str (default:= None)
         URI for entity. For new entities the URI is None, as the knowledge graph backend assigns this.
    tenant_rights: TenantAccessRight (default:= None)
        Rights for tenants
    owner: bool (default:= False)
        Is the logged-in user the owner of the entity
    use_for_nel: bool (default:= Ture)
        Use the entity for named entity linking
    use_vector_index: bool (default:= False)
        Use vector index for labels
    use_vector_index_document: bool (default:= False)
        Use vector index for a document
    use_full_text_index: bool (default:= True)
        Use full text index for entity

    ### Static methods

    `from_dict(entity: Dict[str, Any]) ‑> knowledge.base.ontology.ThingObject`
    :   Creates a ThingObject from a dict.
        
        Parameters
        ----------
        entity: Dict[str, Any]
            Dictionary that contains the data of the entity
        
        Returns
        -------
        instance: ThingObject
            The ThingObject that is created from the dict

    `from_import_dict(entity: Dict[str, Any], raise_on_error: bool = False) ‑> knowledge.base.ontology.ThingObject`
    :   Creates a ThingObject from a dict.
        
        Parameters
        ----------
        entity: Dict[str, Any]
            Dictionary that contains the data of the entity
        raise_on_error: bool (default:= False)
            Whether to raise an error if the dict contains unsupported locales or if there is a mismatch in source
            reference id or source system. If False, the errors will be logged as warnings. The entity will still
            be created, but the unsupported locales will be ignored, and in case of a mismatch in source reference
            id or source system, the value from the dict will be used.
        
        Returns
        -------
        instance: ThingObject
            The ThingObject that is created from the dict
        
        Raises
        ------
        ValueError:
            If the dict contains unsupported locales, or if there is a mismatch in source reference id or source system.

    ### Instance variables

    `alias: List[knowledge.base.entity.Label]`
    :   Alternative labels of the concept.

    `concept_type: knowledge.base.ontology.OntologyClassReference`
    :   Concept type.

    `data_properties: Dict[knowledge.base.ontology.OntologyPropertyReference, List[knowledge.base.ontology.DataProperty]]`
    :   Literals of the concept.

    `description: List[knowledge.base.entity.Description]`
    :   Description of the thing (optional).

    `group_ids: List[str]`
    :   List of group ids.

    `image: str | None`
    :   Image depicting the entities (optional).

    `label: List[knowledge.base.entity.Label]`
    :   Labels of the entity.

    `object_properties: Dict[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.ObjectProperty]`
    :   Relations of the concept.

    `ontology_types: Set[str]`
    :   Ontology types. For public entities.

    `owner: bool`
    :   Is the current user the owner of the entity?

    `owner_external_user_id: str | None`
    :   External user id of the owner.

    `owner_id: str | None`
    :   Internal id of the owner.

    `reference_id: str | None`
    :   Default reference id for the entity.

    `source_reference_id: List[knowledge.base.ontology.DataProperty] | None`
    :   Reference id for to the source.

    `source_system: str | None`
    :   Default reference system for the entity.

    `status_flag: knowledge.base.entity.EntityStatus`
    :   Status flag.

    `tenant_access_right: knowledge.base.access.TenantAccessRight`
    :   Access rights for tenant.

    `uri: str | None`
    :   Unique identifier for entity. If the entity is not yet imported into the knowledge graph, the URI is None.

    `use_for_nel: bool`
    :   Use the entity for named entity linking.

    `use_full_text_index: bool`
    :   Use full text index for entity.

    `use_vector_index: bool`
    :   Use vector index for entity.

    `use_vector_index_document: bool`
    :   Use vector index for document.

    `visibility: str | None`
    :   Visibility.

    ### Methods

    `add_alias(self, alias: str, language_code: knowledge.base.language.LocaleCode) ‑> None`
    :   Adding an alias for an entity.
        
        Parameters
        ----------
        alias: str
            Alias
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `add_data_property(self, data_property: knowledge.base.ontology.DataProperty) ‑> None`
    :   Add data property to the entity.
        
        Parameters
        ----------
        data_property: DataProperty
            Data property that is added

    `add_description(self, description: str, language_code: knowledge.base.language.LocaleCode) ‑> None`
    :   Adding the description for entity.
        
        Parameters
        ----------
        description: str
            Description
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `add_label(self, label: str, language_code: knowledge.base.language.LocaleCode) ‑> None`
    :   Adding a label for an entity.
        
        Parameters
        ----------
        label: str
            Label
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `add_relation(self, prop: knowledge.base.ontology.ObjectProperty) ‑> None`
    :   Adding a relation to the entity.
        
        Parameters
        ----------
        prop: ObjectProperty
            Object property that is added

    `add_source_reference_id(self, value: knowledge.base.ontology.DataProperty) ‑> None`
    :   Adding the reference id from the source system of the entity.
        
        Parameters
        -----------
        value: DataProperty
            Adds the source system reference id as a Data Property.
            **Remark:** The data property must have the property type 'wacom:core#sourceReferenceId'.

    `add_source_system(self, value: knowledge.base.ontology.DataProperty) ‑> None`
    :   Adding the source system of the entity.
        
        Parameters
        -----------
        value: DataProperty
            Adds the source system as a Data Property. **Remark:** The data property must have the property type
            'wacom:core#sourceSystem'.

    `alias_lang(self, language_code: knowledge.base.language.LocaleCode | knowledge.base.language.LanguageCode) ‑> List[knowledge.base.entity.Label]`
    :   Get alias for language_code code.
        
        Parameters
        ----------
        language_code: LocaleCode
            Requested language_code code
        Returns
        -------
        aliases: List[Label]
            Returns a list of aliases for a specific language code

    `as_dict(self) ‑> Dict[str, Any]`
    :   This method constructs a dictionary representation of the instance, aggregating
        label information, descriptions, data and object properties, group identifiers,
        and ownership metadata. It is intended for serialization or API responses.
        
        Parameters
        ----------
        self : object
            The instance of the class on which this method is called.
        
        Returns
        -------
        dict
            A dictionary containing the following keys:
        
            * `URI_TAG`: The unique URI of the instance.
            * `IMAGE_TAG`: The image reference associated with the instance.
            * `LABELS_TAG`: A list of label dictionaries obtained from both the
              `label` and `alias` collections.
            * `DESCRIPTIONS_TAG`: A list of description dictionaries.
            * `TYPE_TAG`: The IRI of the instance's concept type.
            * `STATUS_FLAG_TAG`: The string value of the instance's status flag.
            * `DATA_PROPERTIES_TAG`: A dictionary mapping data‑property IRIs to lists
              of their value dictionaries.
            * `OBJECT_PROPERTIES_TAG`: A dictionary mapping object‑property IRIs to
              their value dictionary.
            * `GROUP_IDS`: The list of group identifiers associated with the instance.
            * `OWNER_TAG`: The owner name of the instance.
            * `OWNER_ID_TAG`: The unique identifier of the owner.

    `data_property_lang(self, data_property: knowledge.base.ontology.OntologyPropertyReference, language_code: knowledge.base.language.LocaleCode) ‑> List[knowledge.base.ontology.DataProperty]`
    :   Get data property for language_code code.
        
        Parameters
        ----------
        data_property: OntologyPropertyReference
            Data property.
        language_code: LocaleCode
            Requested language_code code
        Returns
        -------
        data_properties: List[DataProperty]
            Returns a list of data properties for a specific language code

    `default_source_reference_id(self, language_code: knowledge.base.language.LocaleCode = 'en_US') ‑> str | None`
    :   Getting the source reference id for a certain language code.
        
        Parameters
        ----------
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        
        Returns
        -------
        id: str
            Source reference id.

    `default_source_system(self, language_code: knowledge.base.language.LocaleCode = 'en_US') ‑> str | None`
    :   Getting the source system for a certain language code.
        
        Parameters
        ----------
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        
        Returns
        -------
        id: str
            Source system.

    `description_lang(self, language_code: knowledge.base.language.LocaleCode | knowledge.base.language.LanguageCode) ‑> knowledge.base.entity.Description | None`
    :   Get description for entity.
        
        Parameters
        ----------
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        Returns
        -------
        Optional[Description]
            Returns the description for a specific language_code code if it exists, otherwise None.

    `label_lang(self, language_code: knowledge.base.language.LocaleCode | knowledge.base.language.LanguageCode) ‑> knowledge.base.entity.Label | None`
    :   Get a label for language_code code.
        
        Parameters
        ----------
        language_code: LocaleCode
            Requested language_code code
        Returns
        -------
        label: Optional[Label]
            Returns the label for a specific language code

    `remove_alias(self, label: knowledge.base.entity.Label) ‑> None`
    :   Remove alias for an entity if it exists for language.
        
        Parameters
        ----------
        label: Label
            Alias label

    `remove_data_property(self, data_property: knowledge.base.ontology.OntologyPropertyReference) ‑> None`
    :   Remove data property.
        
        Parameters
        ----------
        data_property: OntologyPropertyReference
            Data property to be removed.

    `remove_description(self, language_code: knowledge.base.language.LocaleCode) ‑> None`
    :   Remove description for an entity if it exists for language.
        
        Parameters
        ----------
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `remove_label(self, language_code: knowledge.base.language.LocaleCode) ‑> None`
    :   Remove the label for an entity if it exists for language.
        
        Parameters
        ----------
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `update_alias(self, value: str, language_code: knowledge.base.language.LocaleCode) ‑> None`
    :   Update or creates an alias for a specific language.
        
        Parameters
        ----------
        value: str
            Value to be set
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `update_description(self, value: str, language_code: knowledge.base.language.LocaleCode) ‑> None`
    :   Update or creates a description for a specific language.
        
        Parameters
        ----------
        value: str
            Value to be set
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `update_label(self, value: str, language_code: knowledge.base.language.LocaleCode) ‑> None`
    :   Update or creates a label for a specific language.
        
        Parameters
        ----------
        value: str
            Value to be set
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.