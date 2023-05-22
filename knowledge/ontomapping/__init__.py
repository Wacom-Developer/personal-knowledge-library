# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import enum
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from rdflib import Graph, RDFS, URIRef

from knowledge.base.ontology import OntologyClassReference, OntologyPropertyReference
from knowledge.public.wikidata import WikidataClass

# Classes
TOPIC_CLASS: str = 'wacom:core#Topic'
IS_RELATED: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#isRelated")
# Constants
DBPEDIA_TYPES: str = "dbpedia_types"
WIKIDATA_TYPES: str = "wikidata_types"
OBJECT_PROPERTIES: str = "object_properties"
DATA_PROPERTIES: str = "data_properties"
DOMAIN_PROPERTIES: str = "domain"
CLASSES: str = "classes"
CONTEXT_NAME: str = 'core'
CWD: Path = Path(__file__).parent
CONFIGURATION_FILE: Path = CWD / '../../pkl-cache/ontology_mapping.json'
TAXONOMY_FILE: Path = CWD / '../../pkl-cache/taxonomy_cache.json'
ontology_graph: Graph = Graph()


def subclasses_of(iri: str) -> List[str]:
    global ontology_graph
    sub_classes: List[str] = [str(s) for s, p, o in ontology_graph.triples((None, RDFS.subClassOf, URIRef(iri)))]
    for sub_class in sub_classes:
        sub_classes.extend(subclasses_of(sub_class))
    return sub_classes


class WikidataClassEncoder(json.JSONEncoder):
    """
    Wikidata Class encoder
    ----------------------
    This class encodes a Wikidata class to JSON.
    """
    def default(self, o):
        if isinstance(o, WikidataClass):
            return o.__dict__()
        return json.JSONEncoder.default(self, o)


class ClassConfiguration(object):
    """
    Class configuration
    -------------------
    This class contains the configuration for a class.

    """
    def __init__(self, ontology_class: str):
        self.__ontology_class: str = ontology_class
        self.__wikidata_classes: List[str] = []
        self.__dbpedia_classes: List[str] = []

    @property
    def ontology_class(self) -> str:
        return self.__ontology_class

    @property
    def wikidata_classes(self) -> List[str]:
        """Wikidata classes."""
        return self.__wikidata_classes

    @wikidata_classes.setter
    def wikidata_classes(self, value: List[str]):
        self.__wikidata_classes = value

    @property
    def dbpedia_classes(self) -> List[str]:
        """DBpedia classes."""
        return self.__dbpedia_classes

    @dbpedia_classes.setter
    def dbpedia_classes(self, value: List[str]):
        self.__dbpedia_classes = value

    @property
    def concept_type(self) -> OntologyClassReference:
        return OntologyClassReference.parse(self.__ontology_class)

    def __str__(self):
        return f'ClassConfiguration(ontology_class={self.__ontology_class}, ' \
               f'wikidata_classes={self.__wikidata_classes}, dbpedia_classes={self.__dbpedia_classes})'


class PropertyType(enum.Enum):
    """
    Property type
    """
    DATA_PROPERTY = 0
    OBJECT_PROPERTY = 1


class PropertyConfiguration(object):
    """
    Property configuration.
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
    """

    def __init__(self, iri: str, property_type: PropertyType, pids: Optional[List[str]] = None):
        self.__iri: str = iri
        self.__pids: List[str] = pids if pids else []
        self.__property: PropertyType = property_type
        self.__inverse: Optional[str] = None
        self.__ranges: List[str] = []
        self.__domains: List[str] = []

    @property
    def iri(self) -> str:
        """IRI of the property."""
        return self.__iri

    @iri.setter
    def iri(self, value: str):
        self.__iri = value

    @property
    def inverse(self) -> Optional[str]:
        """Inverse property."""
        return self.__inverse

    @inverse.setter
    def inverse(self, value: str):
        self.__inverse = value

    @property
    def type(self) -> PropertyType:
        return self.__property

    @property
    def pids(self) -> List[str]:
        """List of property PIDs."""
        return self.__pids

    @property
    def ranges(self) -> List[str]:
        """List of ranges."""
        return self.__ranges

    @property
    def domains(self) -> List[str]:
        """List of domains."""
        return self.__domains

    def __str__(self):
        return f'PropertyConfiguration(ontology_property={self.iri})'


class MappingConfiguration(object):
    """
    Mapping configuration
    ---------------------
    This class contains the configuration for the mapping.

    """

    def __init__(self):
        self.__classes: List[ClassConfiguration] = []
        self.__properties: List[PropertyConfiguration] = []
        self.__index: Dict[str, int] = {}
        self.__index_properties: Dict[str, int] = {}

    @property
    def classes(self) -> List[ClassConfiguration]:
        """List of classes."""
        return self.__classes

    @property
    def properties(self) -> List[PropertyConfiguration]:
        """List of properties."""
        return self.__properties

    def guess_classed(self, classes: List[str]) -> Optional[ClassConfiguration]:
        """
        Guesses the class from the label.
        Parameters
        ----------
        classes: List[str]
            The list of classes

        Returns
        -------
        class: Optional[ClassConfiguration]
            If a mapping exists, the class configuration, otherwise None.
        """
        for cls_name in classes:
            if cls_name in self.__index:
                return self.__classes[self.__index[cls_name]]
        return None

    def guess_property(self, property_pid: str, concept_type: OntologyClassReference) \
            -> Optional[PropertyConfiguration]:
        """
        Guesses the property from the label.
        Parameters
        ----------
        property_pid: str
            PID of the property
        concept_type: OntologyClassReference
            The concept type.
        Returns
        -------
        property: Optional[PropertyConfiguration]
            If a mapping exists, the property configuration, otherwise None.
        """
        if property_pid in self.__index_properties:
            prop_conf: PropertyConfiguration = self.__properties[self.__index_properties[property_pid]]
            if concept_type.iri in prop_conf.domains or 'wacom:core#Thing' in prop_conf.domains:
                return prop_conf
        return None

    def property_for(self, class_ref: OntologyClassReference, property_type: Optional[PropertyType]) \
            -> List[PropertyConfiguration]:
        """
        Returns the properties for a class.
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
        """
        global ontology_graph
        domain_classes: List[str] = [class_ref.iri]
        domain_classes += subclasses_of(class_ref.iri)
        domain_subclasses: Dict[str, List[str]] = {}
        properties: List[PropertyConfiguration] = []
        for prop_conf in self.properties:
            for d in prop_conf.domains:
                if d not in domain_subclasses:
                    domain_subclasses[d] = [d] + subclasses_of(d)
                if class_ref.iri in domain_subclasses[d]:
                    if property_type is None or prop_conf.type == property_type:
                        properties.append(prop_conf)
        return properties

    def add_class(self, class_configuration: ClassConfiguration):
        """
        Adds a class configuration.

        Parameters
        ----------
        class_configuration: ClassConfiguration
            The class configuration
        """
        self.__classes.append(class_configuration)
        for c in class_configuration.wikidata_classes:
            self.__index[c] = len(self.__classes) - 1
        for c in class_configuration.dbpedia_classes:
            self.__index[c] = len(self.__classes) - 1

    def add_property(self, property_configuration: PropertyConfiguration):
        """
        Adds a property configuration.

        Parameters
        ----------
        property_configuration: PropertyConfiguration
            The property configuration
        """
        self.__properties.append(property_configuration)
        for pid in property_configuration.pids:
            self.__index_properties[pid] = len(self.__properties) - 1

    def __str__(self):
        return f"Mapping Configuration(#classes={len(self.__classes)}" \
               f", #properties={len(self.__properties)})"


def build_configuration(mapping: Dict[str, Any]) -> MappingConfiguration:
    """
    Builds the configuration from the mapping file.
    Parameters
    ----------
    mapping: Dict[str, Any]
        The mapping file

    Returns
    -------
    conf: MappingConfiguration
        The mapping configuration
    """
    conf: MappingConfiguration = MappingConfiguration()
    for c, c_conf in mapping['classes'].items():
        class_config: ClassConfiguration = ClassConfiguration(c)
        class_config.dbpedia_classes = c_conf[DBPEDIA_TYPES]
        class_config.wikidata_classes = c_conf[WIKIDATA_TYPES]
        conf.add_class(class_config)
    for p, p_conf in mapping['data_properties'].items():
        property_config: PropertyConfiguration = PropertyConfiguration(p, PropertyType.DATA_PROPERTY,
                                                                       p_conf['wikidata_types'])
        if 'ranges' in p_conf:
            property_config.ranges.extend(p_conf['ranges'])
        if 'domains' in p_conf:
            property_config.domains.extend(p_conf['domains'])
        conf.add_property(property_config)
    for p, p_conf in mapping['object_properties'].items():
        property_config: PropertyConfiguration = PropertyConfiguration(p, PropertyType.OBJECT_PROPERTY,
                                                                       p_conf['wikidata_types'])
        if 'ranges' in p_conf:
            property_config.ranges.extend(p_conf['ranges'])
        if 'domains' in p_conf:
            property_config.domains.extend(p_conf['domains'])
        if 'inverse' in p_conf:
            property_config.inverse = p_conf['inverse']
        conf.add_property(property_config)
    return conf


def update_taxonomy_cache():
    """
    Updates the taxonomy cache.
    """
    global taxonomy_cache
    with open(TAXONOMY_FILE, 'w') as f:
        f.write(json.dumps(taxonomy_cache, indent=2, cls=WikidataClassEncoder))


def register_ontology(rdf_str: str):
    """
    Registers the ontology.
    Parameters
    ----------
    rdf_str: str
        The ontology in RDF/XML format.
    """
    global ontology_graph
    ontology_graph.parse(data=rdf_str, format='xml')


# Mapping configuration
mapping_configuration: Optional[MappingConfiguration] = None
taxonomy_cache: Optional[Dict[str, WikidataClass]] = None

if mapping_configuration is None and CONFIGURATION_FILE.exists():
    configuration = json.loads(CONFIGURATION_FILE.open('r').read())
    mapping_configuration = build_configuration(configuration)

if taxonomy_cache is None:
    if TAXONOMY_FILE.exists():
        try:
            taxonomy = json.loads(TAXONOMY_FILE.open('r').read())
        except json.decoder.JSONDecodeError:
            taxonomy = {}
        taxonomy_cache = {}
        for qid, data in taxonomy.items():
            if data:
                taxonomy_cache[qid] = WikidataClass.create_from_dict(data)
    else:
        taxonomy_cache = {}
