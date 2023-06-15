Module knowledge.base.ontology
==============================

Variables
---------

    
`INVERSE_DATA_PROPERTY_TYPE_MAPPING: dict[str, knowledge.base.ontology.DataPropertyType]`
:   Maps the string representation of the XSD data types to the data types enum constants.

Classes
-------

`Comment(text: str, language_code: knowledge.base.entity.LanguageCode = 'en')`
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

    `create_from_dict(dict_description: dict[str, typing.Any]) ‑> knowledge.base.ontology.Comment`
    :   Create a comment from a dictionary.
        Parameters
        ----------
        dict_description: dict[str, Any]
            Dictionary containing the comment
        
        Returns
        -------
        instance: Comment
            Instance of comment

    `create_from_list(param: list[dict[str, typing.Any]]) ‑> list['Comment']`
    :   Create a list of comments from a list of dictionaries.
        Parameters
        ----------
        param: list[dict[str, Any]]
            List of dictionaries containing the comments
        
        Returns
        -------
        instances: list[Comment]
            List of instances of comments

`DataProperty(content: Any, property_ref: knowledge.base.ontology.OntologyPropertyReference, language_code: knowledge.base.entity.LanguageCode = 'en_US', data_type: knowledge.base.ontology.DataPropertyType = None)`
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
    data_type: str
        Data type

    ### Ancestors (in MRO)

    * knowledge.base.ontology.EntityProperty
    * abc.ABC

    ### Static methods

    `create_from_dict(data_property_struct: dict)`
    :   Create data property from dictionary.
        
        Parameters
        ----------
        data_property_struct: dict
            Dictionary containing data property information.
        
        Returns
        -------
        instance: DataProperty
            Data property instance.

    `create_from_list(param: list[dict]) ‑> list['DataProperty']`
    :   Create data property list from dictionary list.
        
        Parameters
        ----------
        param: list[dict]
            List of dictionaries containing data property information.
        
        Returns
        -------
        instances: list[DataProperty]
            List of data property instances.

    ### Instance variables

    `data_property_type: knowledge.base.ontology.OntologyPropertyReference`
    :   Ontology type.

    `data_type: Optional[knowledge.base.ontology.DataPropertyType]`
    :   Data type (optional).

    `language_code: knowledge.base.entity.LanguageCode`
    :   Language code of the content.

    `value: Any`
    :   Content of the data property.

`DataPropertyType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   DataPropertyType.
    -----------------
    Data types that are used by Datatype properties.

    ### Ancestors (in MRO)

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

`EntityProperty()`
:   EntityProperty
    --------------
    Abstract class for the different types of properties.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.base.ontology.DataProperty
    * knowledge.base.ontology.ObjectProperty

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

    ### Ancestors (in MRO)

    * abc.ABC

    ### Static methods

    `from_dict(entity: dict[str, typing.Any]) ‑> knowledge.base.ontology.InflectionSetting`
    :   Create inflection setting from dictionary.
        Parameters
        ----------
        entity: dict[str, Any]
            Entity dictionary
        
        Returns
        -------
        instance: InflectionSetting
            Inflection setting instance

    ### Instance variables

    `case_sensitive: bool`
    :   Are entity labels of the class treated case-sensitive.

    `concept: knowledge.base.ontology.OntologyClassReference`
    :   Concept class.

    `inflection: str`
    :   Inflection setting

`ObjectProperty(relation: knowledge.base.ontology.OntologyPropertyReference, incoming: Optional[list[typing.Union[str, ForwardRef('ThingObject')]]] = None, outgoing: Optional[list[typing.Union[str, ForwardRef('ThingObject')]]] = None)`
:   Object Property
    ---------------
    ObjectProperty for entities.
    
    Parameter
    ---------
    relation: OntologyPropertyReference
        OntologyPropertyReference type
    incoming: list[str] (default:= [])
        Incoming relations
    outgoing: list[str] (default:= [])
        Outgoing relations

    ### Ancestors (in MRO)

    * knowledge.base.ontology.EntityProperty
    * abc.ABC

    ### Static methods

    `create_from_dict(relation_struct: dict[str, typing.Any]) ‑> tuple[knowledge.base.ontology.OntologyPropertyReference, 'ObjectProperty']`
    :   Create object property from dictionary.
        
        Parameters
        ----------
        relation_struct: dict[str, Any]
            Dictionary containing object property information.
        
        Returns
        -------
        relation_type: OntologyPropertyReference
            OntologyPropertyReference type

    `create_from_list(param: list[dict]) ‑> dict[knowledge.base.ontology.OntologyPropertyReference, 'ObjectProperty']`
    :   Create object property list from dictionary list.
        Parameters
        ----------
        param: list[dict]
            List of dictionaries containing object property information.
        
        Returns
        -------
        instances: dict[OntologyPropertyReference, ObjectProperty]
            Dictionary of object property instances.

    ### Instance variables

    `incoming_relations: list[typing.Union[str, knowledge.base.ontology.ThingObject]]`
    :   Incoming relation

    `outgoing_relations: list[typing.Union[str, knowledge.base.ontology.ThingObject]]`
    :   Outgoing relation

    `relation: knowledge.base.ontology.OntologyPropertyReference`
    :   Reference from the ontology.

`Ontology()`
:   Ontology
    --------
    The ontology consists of classes and properties.

    ### Instance variables

    `classes: list[knowledge.base.ontology.OntologyClass]`
    :   All classes.

    `data_properties: list[knowledge.base.ontology.OntologyProperty]`
    :   All data properties.

    `object_properties: list[knowledge.base.ontology.OntologyProperty]`
    :   All object properties.

    ### Methods

    `add_class(self, class_obj: knowledge.base.ontology.OntologyClass)`
    :   Adding class object.
        
        Parameters
        ----------
        class_obj: OntologyClass
            Class object

    `add_properties(self, prop_obj: knowledge.base.ontology.OntologyProperty)`
    :   Adding properties.
        
        Parameters
        ----------
        prop_obj: OntologyProperty

    `data_properties_for(self, cls_reference: knowledge.base.ontology.OntologyClassReference) ‑> list[knowledge.base.ontology.OntologyPropertyReference]`
    :   Retrieve a list of data properties.
        
        Parameters
        ----------
        cls_reference: OntologyClassReference
            Class of the ontology
        
        Returns
        -------
        data_properties: list[OntologyPropertyReference]
            List of data properties, where domain fit for the class of one of its super classes.

    `get_class(self, class_reference: knowledge.base.ontology.OntologyClassReference) ‑> Optional[knowledge.base.ontology.OntologyClass]`
    :   Get class instance by reference.
        
        Parameters
        ----------
        class_reference: OntologyClassReference
            Class reference
        
        Returns
        --------
        instance: Optional[OntologyClass]
            Instance of ontology class.

    `get_data_properties(self, property_reference: knowledge.base.ontology.OntologyPropertyReference) ‑> Optional[knowledge.base.ontology.OntologyProperty]`
    :   Get object property instance by reference.
        
        Parameters
        ----------
        property_reference: OntologyPropertyReference
            Property reference
        
        Returns
        --------
        instance: Optional[OntologyProperty]
            Instance of ontology object property.

    `get_object_properties(self, property_reference: knowledge.base.ontology.OntologyPropertyReference) ‑> Optional[knowledge.base.ontology.OntologyProperty]`
    :   Get object property instance by reference.
        
        Parameters
        ----------
        property_reference: OntologyPropertyReference
            Property reference
        
        Returns
        --------
        instance: Optional[OntologyProperty]
            Instance of ontology object property.

    `object_properties_for(self, cls_reference: knowledge.base.ontology.OntologyClassReference) ‑> list[knowledge.base.ontology.OntologyPropertyReference]`
    :   Retrieve a list of object properties.
        
        Parameters
        ----------
        cls_reference: OntologyClassReference
            Class of the ontology
        
        Returns
        -------
        object_properties: list[OntologyPropertyReference]
            List of object properties, where domain fit for the class of one of its super classes.

`OntologyClass(tenant_id: str, context: str, reference: knowledge.base.ontology.OntologyClassReference, subclass_of: knowledge.base.ontology.OntologyClassReference = None, icon: Optional[str] = None, labels: Optional[list[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[list[knowledge.base.ontology.Comment]] = None)`
:   OntologyClass
    ----------------
    Concept for ontology.
    
    Parameters
    ----------
    tenant_id: str
        Tenant id for ontology
    context: str
        Context
    reference: OntologyClassReference
        Reference for ontology class
    icon: str
        Icon representing concept
    labels: list[Label]
        List of labels
    comments: list[Comment]
        List of comments
    
    subclass_of: str (default: None)
        Subclass of ontology class

    ### Ancestors (in MRO)

    * knowledge.base.ontology.OntologyObject
    * abc.ABC

    ### Static methods

    `from_dict(concept_dict: dict[str, typing.Any])`
    :   Create OntologyClass from dictionary.
        
        Parameters
        ----------
        concept_dict: dict[str, Any]
            Dictionary containing the concept data.
        
        Returns
        -------
        instance: OntologyClass
            Instance of OntologyClass object.

    `new() ‑> knowledge.base.ontology.OntologyClass`
    :   Create new ontology class.
        
        Returns
        -------
        instance: OntologyClass
            New ontology class.

    ### Instance variables

    `reference: knowledge.base.ontology.OntologyClassReference`
    :   Reference of ontology class.

    `subclass_of: Optional[knowledge.base.ontology.OntologyClassReference]`
    :   Superclass of the class.

`OntologyClassReference(scheme: str, context: str, class_name: str)`
:   Ontology class type
    -------------------
    Associated to an ontology class.
    
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

    `class_name`
    :   Class name.

`OntologyContext(cid: str, tenant_id: str, name: str, icon: str, labels: list[knowledge.base.ontology.OntologyLabel], comments: list[knowledge.base.ontology.Comment], date_added: datetime.datetime, date_modified: datetime.datetime, context: str, base_uri: str, version: int, orphaned: bool, concepts: list[str], properties: list[str])`
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
    labels: list[Label]
        List of labels
    comments: list[Comment]
        List of comments
    context: str
        context name
    base_uri: str
        Base URI
    concepts: list[str]
        List of classes / concepts
    properties: list[str]
        List of properties (data and object properties)

    ### Ancestors (in MRO)

    * knowledge.base.ontology.OntologyObject
    * abc.ABC

    ### Static methods

    `from_dict(context_dict: dict[str, typing.Any])`
    :   Create OntologyContext from dictionary.
        
        Parameters
        ----------
        context_dict: dict[str, Any]
            Dictionary containing the context data.
        
        Returns
        -------
        instance: OntologyContext
            Instance of OntologyContext object.

    ### Instance variables

    `base_uri: str`
    :   Base URI.

    `concepts: list[str]`
    :   List of concepts.

    `date_added: datetime.datetime`
    :   Date added.

    `date_modified: datetime.datetime`
    :   Date modified.

    `id: str`
    :   Context id.

    `orphaned: bool`
    :   Orphaned.

    `properties: list[str]`
    :   List of properties.

    `version: int`
    :   Version.

`OntologyContextSettings(rdf_prefix: str, rdfs_prefix: str, owl_prefix: str, base_literal_uri: str, base_class_uri: str, description_literal_name: str, depth: int)`
:   OntologyContextSettings
    -----------------------
    Describes the settings of the context, such as:
    - prefixes for RDF, RDFS and OWL
    - Base literal URI
    - Base class URI
    - Description literal name
    - depth

    ### Instance variables

    `base_class_uri`
    :   Base class URI.

    `base_literal_uri`
    :   Base literal URI.

    `depth: int`
    :   Depth.

    `description_literal_name: str`
    :   Literal name of the description.

    `owl_prefix`
    :   OWL prefix

    `rdf_prefix`
    :   RDF prefix

    `rdfs_prefix`
    :   RDFS prefix

`OntologyLabel(content: str, language_code: knowledge.base.entity.LanguageCode = 'en', main: bool = False)`
:   Ontology Label
    --------------
    Label that is multi-lingual.
    
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

    `create_from_dict(dict_label: dict[str, typing.Any], tag_name: str = 'value', locale_name: str = 'locale') ‑> knowledge.base.ontology.OntologyLabel`
    :   Create a label from a dictionary.
        
        Parameters
        ----------
        dict_label: dict[str, Any]
            Dictionary with the label information
        tag_name: str
            Tag name of the content
        locale_name: str
            Tag name of the language code
        
        Returns
        -------
        instance: OntologyLabel
            Instance of the label

    `create_from_list(param: list[dict]) ‑> list['LocalizedContent']`
    :   Create a list of labels from a list of dictionaries.
        Parameters
        ----------
        param: list[dict]
            List of dictionaries with the label information
        
        Returns
        -------
        instances: list[OntologyLabel]
            List of label instances

    ### Instance variables

    `main: bool`
    :   Flag if the content is the  main content or an alias.

`OntologyObject(tenant_id: str, iri: str, icon: str, labels: list[knowledge.base.ontology.OntologyLabel], comments: list[knowledge.base.ontology.Comment], context: str)`
:   Generic ontology object
    -----------------------
    
    Parameters
    ----------
    tenant_id: str
        Reference id for tenant
    iri: str
        IRI of the ontology object
    icon: str
        Icon assigned to object, visually representing it
    labels: list[Label]
        List of multi-language_code labels
    comments: list[Label]
        List of multi-language_code comments
    context: str
        Context

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.base.ontology.OntologyClass
    * knowledge.base.ontology.OntologyContext
    * knowledge.base.ontology.OntologyProperty

    ### Instance variables

    `comments: list[knowledge.base.ontology.Comment]`
    :   Comment related to ontology object.

    `context: str`
    :   Context.

    `icon: str`
    :   Icon.

    `iri: str`
    :   IRI

    `labels: list[knowledge.base.ontology.OntologyLabel]`
    :   Labels related to ontology object.

    `tenant_id: str`
    :   Tenant id.

    ### Methods

    `comment_for_lang(self, language_code: knowledge.base.entity.LanguageCode) ‑> Optional[knowledge.base.ontology.Comment]`
    :   Get comment for language_code.
        Parameters
        ----------
        language_code: LanguageCode
            Language code
        
        Returns
        -------
        comment: Optional[Comment]
            Comment for language_code

    `label_for_lang(self, language_code: knowledge.base.entity.LanguageCode) ‑> Optional[knowledge.base.ontology.OntologyLabel]`
    :   Get label for language_code.
        Parameters
        ----------
        language_code: LanguageCode
            Language code
        
        Returns
        -------
        label: Optional[OntologyLabel]
            Label for language_code

`OntologyObjectReference(scheme: str, context: str, name: str)`
:   Ontology class type
    ------------------
    Associated to an entity to link the type of the entity.
    
    Parameters
    ----------
    scheme: str
        Scheme or owner of the ontology object
    context: str
        Context of ontology object
    name: str
        Ontology object reference name

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * knowledge.base.ontology.OntologyClassReference
    * knowledge.base.ontology.OntologyPropertyReference

    ### Static methods

    `parse_iri(iri: str) ‑> tuple[str, str, str]`
    :   Parse an IRI into its components.
        
        Parameters
        ----------
        iri: str
            IRI to parse
        
        Returns
        -------
        tuple[str, str, str]
            Scheme, context and name of the IRI

    ### Instance variables

    `context`
    :   Context.

    `iri`
    :   Internationalized Resource Identifier (IRI) encoded ontology class name.

    `name`
    :   Name.

    `scheme`
    :   Scheme.

`OntologyProperty(kind: knowledge.base.ontology.PropertyType, tenant_id: str, context: str, name: knowledge.base.ontology.OntologyPropertyReference, icon: str = None, property_domain: Optional[list[knowledge.base.ontology.OntologyClassReference]] = None, property_range: Optional[list[typing.Union[knowledge.base.ontology.OntologyClassReference, knowledge.base.ontology.DataPropertyType]]] = None, labels: Optional[list[knowledge.base.ontology.OntologyLabel]] = None, comments: Optional[list[knowledge.base.ontology.Comment]] = None, sub_property_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None, inverse_property_of: Optional[knowledge.base.ontology.OntologyPropertyReference] = None)`
:   Ontology Property
    -----------------
    Property ontology object.
    
    Parameters
    ----------
    kind: str
        Kind of relation
    tenant_id: str
        Tenant id
    context: str
        Context
    name: OntologyPropertyReference
        Name of property object
    icon: str
        Icon describing the property
    property_domain: OntologyClassReference
        Domain for the property
    property_range: OntologyClassReference
        Range for the property
    labels: list[Label]
        List of labels (localized)
    comments: list[Comment],
        List of comments
    sub_property_of: str (default: = None)
        Sub property of.
    inverse_property_of: str (optional)
        Inverse property

    ### Ancestors (in MRO)

    * knowledge.base.ontology.OntologyObject
    * abc.ABC

    ### Static methods

    `from_dict(property_dict: dict[str, typing.Any])`
    :   Create ontology property from dictionary.
        Parameters
        ----------
        property_dict: dict[str, Any]
            Dictionary containing property information.
        
        Returns
        -------
        instance: OntologyProperty
            Ontology property instance.

    `new(kind: knowledge.base.ontology.PropertyType) ‑> knowledge.base.ontology.OntologyProperty`
    :   Create new ontology property.
        Parameters
        ----------
        kind: PropertyType
            Kind of property.
        
        Returns
        -------
        instance: OntologyProperty
            New ontology property.

    ### Instance variables

    `domains: list[knowledge.base.ontology.OntologyClassReference]`
    :   Domain of the property.

    `inverse_property_of: knowledge.base.ontology.OntologyPropertyReference`
    :   Reference to the inverse property

    `is_data_property: bool`
    :   Check if property is data property.
        
        Returns
        -------
        is_data_property: bool
            True if property is data property, False otherwise.

    `kind: knowledge.base.ontology.PropertyType`
    :   Kind of the property.

    `ranges: list[typing.Union[knowledge.base.ontology.OntologyClassReference, knowledge.base.ontology.DataPropertyType]]`
    :   Ranges of the property.

    `reference: knowledge.base.ontology.OntologyPropertyReference`
    :   Reference to property

    `subproperty_of: knowledge.base.ontology.OntologyPropertyReference`
    :   Reference to the super property

`OntologyPropertyReference(scheme: str, context: str, property_name: str)`
:   Property reference
    ------------------
    Associated to an ontology property.
    
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

    `property_name`
    :   Property name.

`PropertyType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   PropertyType
    -----------
    Within the ontology two different property types are defined. A data- and an object property.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `DATA_PROPERTY`
    :

    `OBJECT_PROPERTY`
    :

`ThingEncoder(*, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, default=None)`
:   Thing encoder
    -------------
    Encoder for ThingObject, Label and Description objects.
    
    Constructor for JSONEncoder, with sensible defaults.
    
    If skipkeys is false, then it is a TypeError to attempt
    encoding of keys that are not str, int, float or None.  If
    skipkeys is True, such items are simply skipped.
    
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

    `default(self, o)`
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
                return JSONEncoder.default(self, o)

`ThingObject(label: list[knowledge.base.entity.Label] = None, concept_type: knowledge.base.ontology.OntologyClassReference = wacom:core#Thing, description: Optional[list[knowledge.base.entity.Description]] = None, uri: Optional[str] = None, icon: Optional[str] = None, tenant_rights: knowledge.base.access.TenantAccessRight = [], owner: bool = True, use_for_nel: bool = True)`
:   ThingObject
    -----------
    Generic entity within knowledge graph.
    
    Each entity is derived from this object, thus all entity shares:
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
    label: list[Label]
        List of labels
    icon: str (optional)
        Icon
    description: list[Description] (optional)
        List of descriptions
    concept_type: OntologyClassReference
        Type of the concept
    uri: str
         URI for entity. For new entities the URI is None, as the knowledge graph backend assigns this.
    tenant_rights: TenantAccessRight
        Rights for tenants
    owner: bool
        Is the logged-in user the owner of the entity

    ### Ancestors (in MRO)

    * abc.ABC

    ### Static methods

    `from_dict(entity: dict[str, typing.Any]) ‑> knowledge.base.ontology.ThingObject`
    :   Creates a ThingObject from a dict.
        
        Parameters
        ----------
        entity: dict[str, Any]
            Dictionary that contains the data of the entity
        
        Returns
        -------
        instance: ThingObject
            ThingObject that is created from the dict

    `from_import_dict(entity: dict[str, typing.Any]) ‑> knowledge.base.ontology.ThingObject`
    :   Creates a ThingObject from a dict.
        
        Parameters
        ----------
        entity: dict[str, Any]
            Dictionary that contains the data of the entity
        
        Returns
        -------
        instance: ThingObject
            ThingObject that is created from the dict

    ### Instance variables

    `alias: list[knowledge.base.entity.Label]`
    :   Alternative labels of the concept.

    `concept_type: knowledge.base.ontology.OntologyClassReference`
    :   Concept type.

    `data_properties: dict[knowledge.base.ontology.OntologyPropertyReference, list[knowledge.base.ontology.DataProperty]]`
    :   Literals of the concept.

    `description: Optional[list[knowledge.base.entity.Description]]`
    :   Description of the thing (optional).

    `group_ids: list[str]`
    :   List of group ids.

    `image: Optional[str]`
    :   Image depicting the entities (optional).

    `label: list[knowledge.base.entity.Label]`
    :   Labels of the entity.

    `object_properties: dict[knowledge.base.ontology.OntologyPropertyReference, knowledge.base.ontology.ObjectProperty]`
    :   Relations of the concept.

    `ontology_types: set[str]`
    :   Ontology types. For public entities.

    `owner: bool`
    :   Is current user the owner of the entity.

    `owner_id: str`
    :   Internal id of the owner.

    `reference_id: Optional[str]`
    :   Default reference id for the entity.

    `source_reference_id: Optional[list[knowledge.base.ontology.DataProperty]]`
    :   Reference id for to the source.

    `source_system: Optional[str]`
    :   Default reference system for the entity.

    `status_flag: knowledge.base.entity.EntityStatus`
    :   Status flag.

    `tenant_access_right: knowledge.base.access.TenantAccessRight`
    :   Access rights for tenant.

    `uri: str`
    :   Unique identifier for entity.

    `use_for_nel: bool`
    :   Use the entity for named entity linking.

    `visibility: str`
    :   Visibility.

    ### Methods

    `add_alias(self, alias: str, language_code: knowledge.base.entity.LanguageCode)`
    :   Adding an alias for entity.
        
        Parameters
        ----------
        alias: str
            Alias
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `add_data_property(self, data_property: knowledge.base.ontology.DataProperty)`
    :   Add data property to the entity.
        
        Parameters
        ----------
        data_property: DataProperty
            Data property that is added

    `add_description(self, description: str, language_code: knowledge.base.entity.LanguageCode)`
    :   Adding the description for entity.
        
        Parameters
        ----------
        description: str
            Description
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `add_label(self, label: str, language_code: knowledge.base.entity.LanguageCode)`
    :   Adding a label for entity.
        
        Parameters
        ----------
        label: str
            Label
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `add_relation(self, prop: knowledge.base.ontology.ObjectProperty)`
    :   Adding a relation to the entity.
        
        Parameters
        ----------
        prop: ObjectProperty
            Object property that is added

    `add_source_reference_id(self, value: knowledge.base.ontology.DataProperty)`
    :   Adding the reference id from the source system of the entity.
        
        Parameters
        -----------
        value: DataProperty
            Adds the source system reference id as a Data Property.
            **Remark:** The data property must have the property type 'wacom:core#sourceReferenceId'.

    `add_source_system(self, value: knowledge.base.ontology.DataProperty)`
    :   Adding the source system  of the entity.
        
        Parameters
        -----------
        value: DataProperty
            Adds the source system as a Data Property. **Remark:** The data property must have the property type
            'wacom:core#sourceSystem'.

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

    `data_property_lang(self, data_property: knowledge.base.ontology.OntologyPropertyReference, language_code: knowledge.base.entity.LanguageCode) ‑> list[knowledge.base.ontology.DataProperty]`
    :   Get data property for language_code code.
        
        Parameters
        ----------
        data_property: OntologyPropertyReference
            Data property.
        language_code: LanguageCode
            Requested language_code code
        Returns
        -------
        data_properties: list[DataProperty]
            Returns a list of data properties for a specific language code

    `default_source_reference_id(self, language_code: knowledge.base.entity.LanguageCode = 'en_US') ‑> Optional[str]`
    :   Getting the source reference id for a certain language code.
        
        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        
        Returns
        -------
        id: str
            Source reference id.

    `default_source_system(self, language_code: knowledge.base.entity.LanguageCode = 'en_US') ‑> Optional[str]`
    :   Getting the source system for a certain language code.
        
        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        
        Returns
        -------
        id: str
            Source system.

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

    `label_lang(self, language_code: knowledge.base.entity.LanguageCode) ‑> Optional[knowledge.base.entity.Label]`
    :   Get label for language_code code.
        
        Parameters
        ----------
        language_code: LanguageCode
            Requested language_code code
        Returns
        -------
        label: Optional[Label]
            Returns the label for a specific language code

    `remove_alias(self, label: knowledge.base.entity.Label)`
    :   Remove alias for entity if it exists for language.
        
        Parameters
        ----------
        label: Label
            Alias label

    `remove_data_property(self, data_property: knowledge.base.ontology.OntologyPropertyReference)`
    :   Remove data property.
        
        Parameters
        ----------
        data_property: OntologyPropertyReference
            Data property to be removed.

    `remove_description(self, language_code: knowledge.base.entity.LanguageCode)`
    :   Remove description for entity if it exists for language.
        
        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `remove_label(self, language_code: knowledge.base.entity.LanguageCode)`
    :   Remove label for entity if it exists for language.
        
        Parameters
        ----------
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `update_alias(self, value: str, language_code: knowledge.base.entity.LanguageCode)`
    :   Update or creates an alias for a specific language.
        
        Parameters
        ----------
        value: str
            Value to be set
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `update_description(self, value: str, language_code: knowledge.base.entity.LanguageCode)`
    :   Update or creates a description for a specific language.
        
        Parameters
        ----------
        value: str
            Value to be set
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.

    `update_label(self, value: str, language_code: knowledge.base.entity.LanguageCode)`
    :   Update or creates a label for a specific language.
        
        Parameters
        ----------
        value: str
            Value to be set
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.