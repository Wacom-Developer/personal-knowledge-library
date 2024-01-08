Module knowledge.ontomapping
============================

Sub-modules
-----------
* knowledge.ontomapping.manager

Functions
---------

    
`build_configuration(mapping: Dict[str, Any]) ‑> knowledge.ontomapping.MappingConfiguration`
:   Builds the configuration from the mapping file.
    Parameters
    ----------
    mapping: Dict[str, Any]
        The mapping file
    
    Returns
    -------
    conf: MappingConfiguration
        The mapping configuration

    
`get_mapping_configuration() ‑> knowledge.ontomapping.MappingConfiguration`
:   Returns the mapping configuration.
    
    Returns
    -------
    mapping_configuration: MappingConfiguration
        The mapping configuration

    
`is_iso_date(date_string: str) ‑> bool`
:   Checks if a date string is an ISO date.
    Parameters
    ----------
    date_string: str
        Date string.
    
    Returns
    -------
    is_iso_date: bool
        True if the date string is an ISO date, otherwise False.

    
`load_configuration(configuration: pathlib.Path = PosixPath('.pkl-cache/ontology_mapping.json'))`
:   Loads the configuration.
    
    Raises
    ------
    ValueError
        If the configuration file is not found.

    
`register_ontology(rdf_str: str)`
:   Registers the ontology.
    Parameters
    ----------
    rdf_str: str
        The ontology in RDF/XML format.

    
`subclasses_of(iri: str) ‑> List[str]`
:   Returns the subclasses of an ontology class.
    Parameters
    ----------
    iri: str
        Ontology class IRI.
    
    Returns
    -------
    subclasses: List[str]
        Subclasses of the ontology class.

    
`update_taxonomy_cache(path: pathlib.Path = PosixPath('.pkl-cache'))`
:   Updates the taxonomy cache.
    
    Parameters
    ----------
    path: Path
        The path to the cache file.

Classes
-------

`ClassConfiguration(ontology_class: str)`
:   Class configuration
    -------------------
    This class contains the configuration for a class.

    ### Instance variables

    `concept_type: knowledge.base.ontology.OntologyClassReference`
    :   Concept type.

    `dbpedia_classes: List[str]`
    :   DBpedia classes.

    `ontology_class: str`
    :   Ontology class.

    `wikidata_classes: List[str]`
    :   Wikidata classes.

`MappingConfiguration()`
:   Mapping configuration
    ---------------------
    This class contains the configuration for the mapping.

    ### Instance variables

    `classes: List[knowledge.ontomapping.ClassConfiguration]`
    :   List of classes.

    `properties: List[knowledge.ontomapping.PropertyConfiguration]`
    :   List of properties.

    ### Methods

    `add_class(self, class_configuration: knowledge.ontomapping.ClassConfiguration)`
    :   Adds a class configuration.
        
        Parameters
        ----------
        class_configuration: ClassConfiguration
            The class configuration

    `add_property(self, property_configuration: knowledge.ontomapping.PropertyConfiguration)`
    :   Adds a property configuration.
        
        Parameters
        ----------
        property_configuration: PropertyConfiguration
            The property configuration

    `check_data_property_range(self, property_type: knowledge.base.ontology.OntologyPropertyReference, content: Optional[Any]) ‑> bool`
    :   Checks if the content is in the range of the property.
        
        Parameters
        ----------
        property_type: OntologyPropertyReference
            The property type
        content: Optional[Any]
            The content
        
        Returns
        -------
        evaluation: bool
            True if the content is in the range, False otherwise.

    `check_object_property_range(self, property_type: knowledge.base.ontology.OntologyPropertyReference, source_type: knowledge.base.ontology.OntologyClassReference, target_type: knowledge.base.ontology.OntologyClassReference) ‑> bool`
    :   Checks if the target is in the range of the property.
        Parameters
        ----------
        property_type: OntologyPropertyReference
            The property
        source_type: OntologyClassReference
            The concept type
        target_type: OntologyClassReference
            The target type
        
        Returns
        -------
        valid: bool
            True if the target is in the range, False otherwise.

    `guess_classed(self, classes: List[str]) ‑> Optional[knowledge.ontomapping.ClassConfiguration]`
    :   Guesses the class from the label.
        Parameters
        ----------
        classes: List[str]
            The list of classes
        
        Returns
        -------
        class: Optional[ClassConfiguration]
            If a mapping exists, the class configuration, otherwise None.

    `guess_property(self, property_pid: str, concept_type: knowledge.base.ontology.OntologyClassReference) ‑> Optional[knowledge.ontomapping.PropertyConfiguration]`
    :   Guesses the property from the label.
        Parameters
        ----------
        property_pid: str
            PID of the property
        concept_type: OntologyClassReference
            The concept type.
        Returns
        -------
        property_config: Optional[PropertyConfiguration]
            If a mapping exists, the property configuration, otherwise None.

    `property_for(self, class_ref: knowledge.base.ontology.OntologyClassReference, property_type: Optional[knowledge.ontomapping.PropertyType]) ‑> List[knowledge.ontomapping.PropertyConfiguration]`
    :   Returns the properties for a class.
        Parameters
        ----------
        class_ref: OntologyClassReference
            The class reference.
        property_type: Optional[PropertyType]
            The property type, if None, all properties are returned.
        Returns
        -------
        properties: List[PropertyConfiguration]
            The list of properties.

    `property_for_iri(self, property_iri: str) ‑> knowledge.ontomapping.PropertyConfiguration`
    :   Returns the property configuration for an IRI.
        
        Parameters
        ----------
        property_iri: str
            The property IRI
        
        Returns
        -------
        property: PropertyConfiguration
            The property configuration
        
        Raises
        ------
        ValueError
            If the property is not found.

`PropertyConfiguration(iri: str, property_type: knowledge.ontomapping.PropertyType, pids: Optional[List[str]] = None)`
:   Property configuration.
    -----------------------
    This class contains the configuration for a property.
    
    Parameters
    ----------
    iri: str
        The IRI of the property.
    property_type: PropertyType
        The property type.
    pids: Optional[List[str]]
        The list of property PIDs.

    ### Instance variables

    `domains: List[str]`
    :   List of domains.

    `inverse: Optional[str]`
    :   Inverse property.

    `iri: str`
    :   IRI of the property.

    `pids: List[str]`
    :   List of property PIDs.

    `ranges: List[str]`
    :   List of ranges.

    `type: knowledge.ontomapping.PropertyType`
    :   Property type.

`PropertyType(*args, **kwds)`
:   Property type

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `DATA_PROPERTY`
    :

    `OBJECT_PROPERTY`
    :

`WikidataClassEncoder(*, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, default=None)`
:   Wikidata Class encoder
    ----------------------
    This class encodes a Wikidata class to JSON.
    
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