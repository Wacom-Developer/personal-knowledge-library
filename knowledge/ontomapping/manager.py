# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from knowledge.base.entity import Label, LanguageCode, Description
from knowledge.base.ontology import ThingObject, DataProperty, SYSTEM_SOURCE_SYSTEM, SYSTEM_SOURCE_REFERENCE_ID, \
    OntologyClassReference, OntologyPropertyReference, ObjectProperty, LANGUAGE_LOCALE_MAPPING
from knowledge.ontomapping import ClassConfiguration, mapping_configuration, TOPIC_CLASS, taxonomy_cache, IS_RELATED, \
    PropertyConfiguration, PropertyType
from knowledge.public.wikidata import WikidataThing, WikiDataAPIClient, WikidataClass
from knowledge.utils.wikipedia import get_wikipedia_summary


def flatten(hierarchy: WikidataClass, use_names: bool = False) -> List[str]:
    """
    Flattens the hierarchy.

    Parameters
    ----------
    hierarchy: WikidataClass
        Hierarchy
    use_names: bool
        Use names instead of QIDs.

    Returns
    -------
    hierarchy: List[str]
        Hierarchy

    """
    hierarchy_list: List[str] = [hierarchy.qid]
    jobs: List[WikidataClass] = [hierarchy]
    while len(jobs) > 0:
        job: WikidataClass = jobs.pop()
        if use_names:
            hierarchy_list.append(f'{job.qid} ({job.label})')
        else:
            hierarchy_list.append(job.qid)
        for c in job.superclasses:
            if use_names:
                if f'{job.qid} ({job.label})' not in hierarchy_list:
                    jobs.append(c)
            else:
                if c.qid not in hierarchy_list:
                    jobs.append(c)
    return hierarchy_list


def wikidata_taxonomy(qid: str) -> Optional[WikidataClass]:
    """
    Returns the taxonomy of a Wikidata thing.
    Parameters
    ----------
    qid: str
        Wikidata QID.

    Returns
    -------
    hierarchy: WikidataClass
        Hierarchy.
    """
    if taxonomy_cache and qid in taxonomy_cache:
        taxonomy: WikidataClass = taxonomy_cache[qid]
        return taxonomy
    hierarchy: WikidataClass = WikiDataAPIClient.superclasses(qid)
    if hierarchy:
        taxonomy_cache[qid] = hierarchy
    return hierarchy


def wikidata_to_thing(wikidata_thing: WikidataThing, all_relations: Dict[str, Any], supported_locales: List[str],
                      pull_wikipedia: bool = False) -> ThingObject:
    """
    Converts a Wikidata thing to a ThingObject.

    Parameters
    ----------
    wikidata_thing: WikidataThing
        Wikidata thing

    all_relations: Dict[str, Any]
        All relations.

    supported_locales: List[str]
        Supported locales.

    pull_wikipedia: bool
        Pull Wikipedia summary.

    Returns
    -------
    thing: ThingObject
        Thing object

    """
    qid: str = wikidata_thing.qid
    labels: List[Label] = [l for l in wikidata_thing.label.values() if str(l.language_code) in supported_locales]
    for lang, aliases in wikidata_thing.aliases.items():
        if str(lang) in supported_locales:
            labels.extend([a for a in aliases])
    descriptions: List[Description] = []
    if 'wiki' in wikidata_thing.sitelinks and pull_wikipedia:
        for lang, title in wikidata_thing.sitelinks['wiki'].titles.items():
            locale: str = LANGUAGE_LOCALE_MAPPING.get(lang, "NOT_SUPPORTED")
            if locale in supported_locales:
                try:
                    descriptions.append(Description(description=get_wikipedia_summary(title, lang),
                                                    language_code=LanguageCode(locale)))
                except Exception as e:
                    logging.error(f'Failed to get Wikipedia summary for {title} ({lang}): {e}')
    if len(descriptions) == 0:
        descriptions = [l for l in wikidata_thing.description.values()]
    # Create the thing
    thing: ThingObject = ThingObject(label=labels,
                                     description=descriptions,
                                     icon=wikidata_thing.image(dpi=500))
    thing.add_source_system(DataProperty(content='wikidata', property_ref=SYSTEM_SOURCE_SYSTEM,
                                         language_code=LanguageCode('en_US')))
    thing.add_source_reference_id(DataProperty(content=qid, property_ref=SYSTEM_SOURCE_REFERENCE_ID,
                                               language_code=LanguageCode('en_US')))
    thing.add_data_property(DataProperty(content=datetime.utcnow().isoformat(),
                                         property_ref=OntologyPropertyReference.parse('wacom:core#lastUpdate')))
    class_configuration: Optional[ClassConfiguration] = None
    class_types: List[str] = wikidata_thing.ontology_types
    for cls in wikidata_thing.instance_of:
        hierarchy: WikidataClass = wikidata_taxonomy(cls.qid)
        if hierarchy:
            class_types.extend(flatten(hierarchy))
    if mapping_configuration:
        class_configuration = mapping_configuration.guess_classed(class_types)
    if class_configuration:
        thing.concept_type = class_configuration.concept_type
    else:
        thing.concept_type = OntologyClassReference.parse(TOPIC_CLASS)
    relation_props: Dict[OntologyPropertyReference, List[str]] = {}
    for pid, cl in wikidata_thing.claims.items():
        prop: Optional[PropertyConfiguration] = mapping_configuration.guess_property(pid, thing.concept_type)
        if prop and prop.type == PropertyType.DATA_PROPERTY:
            property_type: OntologyPropertyReference = OntologyPropertyReference.parse(prop.iri)
            for c in cl.literals:
                if isinstance(c, dict):
                    thing.add_data_property(DataProperty(content=c['value'], property_ref=property_type))
                elif isinstance(c, (str, float, int)):
                    thing.add_data_property(DataProperty(content=c, property_ref=property_type))
    for relation in all_relations.get(qid, []):
        prop: Optional[PropertyConfiguration] = mapping_configuration.guess_property(relation['predicate']['pid'],
                                                                                     thing.concept_type)
        if prop and prop.type == PropertyType.OBJECT_PROPERTY:
            property_type: OntologyPropertyReference = OntologyPropertyReference.parse(prop.iri)
            if property_type not in relation_props:
                relation_props[property_type] = []
            relation_props[property_type].append(relation['target']['qid'])
        else:
            if IS_RELATED not in relation_props:
                relation_props[IS_RELATED] = []
            relation_props[IS_RELATED].append(relation['target']['qid'])

    for p, lst in relation_props.items():
        thing.add_relation(ObjectProperty(p, outgoing=lst))

    return thing
