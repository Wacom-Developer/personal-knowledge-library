# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

import ndjson
from tqdm import tqdm

from knowledge import logger
from knowledge.base.entity import LanguageCode, IMAGE_TAG, DATA_PROPERTIES_TAG, STATUS_FLAG_TAG, Description, Label
from knowledge.base.ontology import SYSTEM_SOURCE_SYSTEM, SYSTEM_SOURCE_REFERENCE_ID, ThingObject, \
    OntologyClassReference, DataProperty, OntologyPropertyReference, ObjectProperty, SUPPORTED_LOCALES
from knowledge.ontomapping.manager import wikidata_to_thing, wikidata_taxonomy
from knowledge.public.relations import wikidata_relations_extractor
from knowledge.public.wikidata import INSTANCE_OF, WikiDataAPIClient, wikidate, IMAGE, WikidataThing, WikidataClass


# -------------------------------------------------- Structures --------------------------------------------------------


class WikidataSyncException(Exception):
    pass


# -------------------------------------------------- Structures --------------------------------------------------------
WACOM_KNOWLEDGE_TAG: str = 'wacom-knowledge'
ICON_TAG: str = 'icon'
DEFAULT_TYPE_TAG: str = "default-type"
ENTITY_LIST_MODE: str = 'entity-list'
SPARQL_QUERY_MODE: str = 'query'
CLASS_MAPPING: str = 'class-mapping'

# Mapping to map the simple language_code code to a default language_code / country code
language_code_mapping: Dict[str, LanguageCode] = {
    'en': LanguageCode('en_US'),
    'ja': LanguageCode('ja_JP'),
    'de': LanguageCode('de_DE'),
    'bg': LanguageCode('bg_BG'),
    'zh': LanguageCode('zh_CN'),
    'fr': LanguageCode('fr_FR'),
    'it': LanguageCode('it_IT')
}


# ----------------------------------------------- Helper functions -----------------------------------------------------
def update_language_code(lang: str):
    return language_code_mapping.get(lang, lang)


def localized_list_description(entity_dict: Dict[str, str]) -> List[Description]:
    return [Description(cont, update_language_code(lang)) for lang, cont in entity_dict.items()]


def localized_list_label(entity_dict: Dict[str, str]) -> List[Label]:
    return [Label(cont, update_language_code(lang), main=True) for lang, cont in entity_dict.items() if cont != '']


def localized_flatten_alias_list(entity_dict: Dict[str, List[str]]) -> List[Label]:
    flatten: List[Label] = []
    for language, items in entity_dict.items():
        for i in items:
            if i != '':
                flatten.append(Label(i, update_language_code(language), main=False))
    return flatten


def from_dict(entity: Dict[str, Any], concept_type: OntologyClassReference) -> ThingObject:
    labels: List[Label] = localized_list_label(entity['label'])
    description: List[Description] = localized_list_description(entity['description'])
    alias: List[Label] = localized_flatten_alias_list(entity['alias'])
    if IMAGE_TAG in entity:
        icon: str = entity[IMAGE_TAG]
    else:
        logger.warning(f"Entity has no image: {entity}")
        icon: str = ''
    # Create the entity
    thing: ThingObject = ThingObject(label=labels, concept_type=concept_type, description=description, icon=icon)
    thing.alias = alias
    if STATUS_FLAG_TAG in entity:
        thing.status_flag = entity[STATUS_FLAG_TAG]
    return thing


# --------------------------------------------------- Utilities --------------------------------------------------------

def strip(url: str) -> str:
    """Strip qid from url.
    :param url: str
        Strip QID from URL
    :return: QID
    """
    parts = url.split('/')
    return parts[-1]


def build_entity(entity: Dict[str, Any], properties: Dict[str, Any], class_mapping: Dict[str, dict],
                 concept_type: Optional[str] = None, linked_to: Optional[str] = None, default_language: str = 'en') \
        -> Tuple[ThingObject, List[Tuple[str, Optional[str], Optional[str]]]]:
    """Builds a ThingObject based on the mapping and properties from Wikidata.

    Parameters
    ----------
    entity: Dict[str, Any] -
        Entity from Wikidata
    properties: Dict[str, Any] -
        Properties from Wikidata
    class_mapping: Dict[str, dict] -
        Class mapping
    concept_type: str, optional -
        Preset concept type
    linked_to: str, optional -
        If the entity is linked to another
    default_language: str
        Default language
    Returns
    -------
    result: ThingObject
        Thing object
    additional_qids: List[str]
        List of additional qids which are added via relation
    """
    qid: str = entity['uri']
    mapping: Dict[str, Any] = {}
    additional_qids: List[Tuple[str, Optional[str], Optional[str]]] = []
    wikidata: WikiDataAPIClient = WikiDataAPIClient()
    if concept_type is None:
        # First check the class of the Wikidata entity for class mapping
        if INSTANCE_OF in properties:
            # Iterate over all classes
            for cls in properties[INSTANCE_OF]['values']:
                wikidata_class: str = cls['id']
                mapping = class_mapping.get(wikidata_class)
                if mapping:
                    break
        # Second, if mapping is None the QID needs to be checked
        if mapping is None:
            mapping = class_mapping.get(qid)
    else:
        for m in class_mapping.values():
            if m[WACOM_KNOWLEDGE_TAG] == concept_type:
                mapping = m
                break

    # Without mapping we ignore the entity
    if mapping is None:
        classes: list = properties[INSTANCE_OF]['values']
        for ent in classes:
            w_class = wikidata.entity(ent['id'])
            #logger.warning('QID: {} -> {} - {}'.format(qid, w_class['uri'], w_class['label']))
        classes_types: list = [c['id'] for c in classes]
        log_mapping_issue(qid, entity['label'].get(default_language), linked_to, classes_types)
        raise WikidataSyncException(f'No mapping existing for qid:= {qid} ({entity["label"]}). '
                                    f'All classes: {classes_types}')
    # Validate that we have a mapping
    if WACOM_KNOWLEDGE_TAG not in mapping:
        raise WikidataSyncException(f'Invalid mapping qid:= {qid} ({entity["label"]}) - mapping:= {mapping}.')
    # Use concept
    concept_type: OntologyClassReference = OntologyClassReference.parse(mapping[WACOM_KNOWLEDGE_TAG])
    # Initialize icon with Wikidata or Wikipedia thumb
    icon: str = entity[IMAGE_TAG]
    # handling of image: Overwrite with different property, e.g., logo
    if ICON_TAG in mapping:
        img_prop: str = mapping[ICON_TAG]
        # Overwrite icon
        if img_prop in properties and len(properties[img_prop]['values']) > 0:
            img_title: str = properties[img_prop]['values'][0]
            icon = WikiDataAPIClient.image_url(img_title)
            entity[IMAGE_TAG] = icon
    # If no mapping overwrite and not icon look for image property
    elif (icon is None or icon == '') and IMAGE in properties:
        img_prop: dict = properties[IMAGE]
        entity[ICON_TAG] = WikiDataAPIClient.image_url(img_prop['values'][0])
    thing: ThingObject = from_dict(entity=entity, concept_type=concept_type)
    thing.add_source_system(DataProperty(content='wikidata', property_ref=SYSTEM_SOURCE_SYSTEM,
                                         language_code=LanguageCode('en_US')))
    thing.add_source_reference_id(DataProperty(content=qid, property_ref=SYSTEM_SOURCE_REFERENCE_ID,
                                               language_code=LanguageCode('en_US')))
    thing.ontology_types = entity['types']
    # Check literals
    for literal in mapping['literals']:
        if literal['wikidata'] in properties:
            p: dict = properties[literal['wikidata']]
            datatype: str = literal.get('type')
            if datatype and datatype == 'float' and len(p['values']) > 0:
                value: dict = p['values'][0]
                thing.add_data_property(
                    DataProperty(str(value['amount']), OntologyPropertyReference.parse(literal[WACOM_KNOWLEDGE_TAG]),
                                 language_code=LanguageCode('en_US')))
            # Special handling of date
            elif datatype and datatype == 'date':
                if 'values' in p and len(p['values']) > 0:
                    date_struct: dict = wikidate(p)
                    value: str = date_struct['time']
                    thing.add_data_property(DataProperty(value,
                                                         OntologyPropertyReference.parse(literal[WACOM_KNOWLEDGE_TAG])))
            # List of values
            elif datatype and datatype == 'list':
                for v in p['values']:
                    thing.add_data_property(DataProperty(v,
                                                         OntologyPropertyReference.parse(literal[WACOM_KNOWLEDGE_TAG])))
            # Pick the first
            elif 'values' in p and len(p['values']) > 0:
                value = p['values'][0]
                value_str: str = ''
                locale: Optional[LanguageCode] = None
                if isinstance(value, str):
                    value_str = value
                if isinstance(value, dict):
                    if 'entity-type' in value:
                        if value['entity-type'] == "item":
                            ent = wikidata.entity(value['id'])
                            value_str = ent['label']
                            locale = LanguageCode('en_US')
                    elif 'text' in value:
                        value_str = value['text']
                        locale = update_language_code(value['language'])
                thing.add_data_property(DataProperty(value_str,
                                                     OntologyPropertyReference.parse(literal[WACOM_KNOWLEDGE_TAG]),
                                                     language_code=locale))

    # Check relations
    for relation in mapping['relations']:
        relation_type: OntologyPropertyReference = OntologyPropertyReference.parse(relation.get(WACOM_KNOWLEDGE_TAG))
        if relation['wikidata'] in properties:
            p: dict = properties[relation['wikidata']]
            outgoing: List[str] = [v['id'] for v in p['values'] if isinstance(v, dict) and 'id' in v]
            additional_qids.extend([(o, relation.get(DEFAULT_TYPE_TAG), qid) for o in outgoing])
            thing.add_relation(ObjectProperty(relation_type, outgoing=outgoing))
    return thing, additional_qids


def build_query(params: Dict[str, Any]) -> List[str]:
    """
    Build of query.

    Parameters
    ----------
    params:
        Parameters for query

    Returns
    -------
    queries: List[str]
        SPARQL query string
    """
    filters: List[Dict[str, Any]] = params.get('filters')
    dynamics: Dict[str, Any] = params.get('dynamic-filters')
    limit: int = params.get('limit', 1000)
    lang_code: str = params.get('language_code', 'en')
    filter_string: str = ''
    queries: List[str] = []
    for f in filters:
        filter_string += "?item wdt:{}  wd:{}.\n".format(f['property'], f['target'])
    if dynamics:
        property_str: str = dynamics["property"]
        for v in dynamics["targets"]:
            dyn: str = filter_string + "?item wdt:{}  wd:{}.\n".format(property_str, v)
            query: str = f"""SELECT DISTINCT ?item ?itemLabel WHERE {{
              {dyn}SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],{lang_code}\". }}
            }}
            LIMIT {limit}
            """
            queries.append(query)
    else:
        query: str = f"""SELECT DISTINCT ?item ?itemLabel WHERE {{
          {filter_string}SERVICE wikibase:label {{ bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],{lang_code}\". }}
        }}
        LIMIT {limit}
        """
        queries.append(query)
    return queries


def log_mapping_issue(qid: str, label: dict, reference_id: Optional[str],  classes: list,
                      logfile: str = 'mapping_issues.ndjson'):
    # Writing items to a ndjson file
    with open(logfile, 'a') as f:
        writer = ndjson.writer(f, ensure_ascii=False)
        writer.writerow({'qid': qid, 'label': label, 'linked_to': reference_id, 'classes': classes})


def cache_entity(thing: ThingObject, path: Path) -> str:
    with path.open('a') as wa:
        writer = ndjson.writer(wa, ensure_ascii=False)
        writer.writerow(thing.__dict__())
    return thing.default_source_reference_id()


def load_qids(cache: Path) -> Tuple[Set[str], Dict[str, int]]:
    qids: Set[str] = set()
    types_mapping: Dict[str, int] = {}
    if cache.exists():
        with cache.open('r') as cf:
            for thing in ndjson.reader(cf):
                try:
                    qids.add(thing[DATA_PROPERTIES_TAG][SYSTEM_SOURCE_REFERENCE_ID.iri][0]['value'])
                except Exception as e:
                    logger.error(e)
                count_type(thing['type'], types_mapping)
    return qids, types_mapping


def count_type(concept_type: str, types_mapping: Dict[str, int]):
    if concept_type not in types_mapping:
        types_mapping[concept_type] = 0
    types_mapping[concept_type] += 1


def check_missing_qids(entities: List[WikidataThing], retrieved_entities: Set[str], mapping: Dict[str, Dict[str, Any]])\
        -> Set[str]:
    for entity in entities:
        for cls in entity.instance_of:
            hierarchy: WikidataClass = wikidata_taxonomy(cls.qid)
            if hierarchy.qid in mapping:
                class_mapping: Dict[str, Any] = mapping[hierarchy.qid]

        for pid in entity:
            if pid in mapping:
                for c in entity.instance_of[pid]:
                    if c.target not in retrieved_entities:
                        print(f"Missing {c.target} for {entity.qid}")
        for pid, cl in entity.claims.items():
            if pid in mapping:
                for c in cl:
                    if c.target not in retrieved_entities:
                        print(f"Missing {c.target} for {entity.qid}")
            print()

    return set()


def main(mapping: Path, cache: Path, default_language: str, languages: List[str] = None):
    """
    Main.

    Arguments
    ---------
    mapping: Path
        Path to mapping file
    cache: Path
        Path to cache file with ThingObjects
    default_language: str
        Default language
    languages: List[str]
        List of languages
    """
    # All failed jobs
    failed_jobs: set = set()
    cached_entities, types_count = load_qids(cache)
    # Mapping of wikidata classes to Wacom Ontology
    class_mapping: Dict[str, Dict[str, Any]] = {}

    with mapping.open('r') as json_file:
        configuration: Dict[str, Any] = json.load(json_file)
        for c in configuration['class-mapping']:
            for qid in c['wikidata']:
                class_mapping[qid] = c
    # List of qids
    qids: Set[str] = set()

    # First query the entry entities
    if SPARQL_QUERY_MODE in configuration:
        queries: list = build_query(configuration[SPARQL_QUERY_MODE])
        for query in queries:
            results: dict = WikiDataAPIClient.sparql_query(query)
            qids.update([item['item']['value'] for item in results['results']['bindings']])
    elif ENTITY_LIST_MODE in configuration:
        qids = set(configuration[ENTITY_LIST_MODE])
    else:
        logger.error("No jobs defined.")
        import sys
        sys.exit(0)
    all_wikidata_things: Dict[str, WikidataThing] = {}
    while len(qids) > 0:
        entities: List[WikidataThing] = WikiDataAPIClient.retrieve_entities(qids)
        for entity in entities:
            all_wikidata_things[entity.qid] = entity
        qids = check_missing_qids(entities, set(all_wikidata_things.keys()), class_mapping)
    relations: Dict[str, Dict[str, Any]] = wikidata_relations_extractor(all_wikidata_things)
    for wiki_thing in all_wikidata_things.values():
        thing = wikidata_to_thing(wiki_thing, relations, SUPPORTED_LOCALES)

    logger.info("{} entities are imported".format(len(all_wikidata_things)))
    analytics: Dict[str, Any] = {
        'ontology': {},
        'wikidata': {},
        'dbpedia': {}
    }
    thing_objects: List[ThingObject] = []
    for qid, w_thing in tqdm(all_wikidata_things.items(),
                             desc=f"Processing {len(all_wikidata_things)} Wikidata entities."):
        thing = wikidata_to_thing(w_thing, relations, SUPPORTED_LOCALES)
        thing_objects.append(thing)

    with Path(cache / 'things.ndjson').open('w') as fp:
        for item in thing_objects:
            fp.write(f"{json.dumps(item.__dict__(), ensure_ascii=False)}\n")
    with Path(cache / 'analytics.json').open('w') as fp:
        json.dump(analytics, fp, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cache", help="Path to output directory.")
    parser.add_argument("-m", "--mapping", help="Ontology mappings.")
    parser.add_argument("-l", "--languages", nargs='+', default=['en'], help="List of languages to import")
    parser.add_argument("-d", "--default_language", default='en', help="Mapping.")
    args = parser.parse_args()
    cache_path: Path = Path(args.cache)
    if not os.path.exists(cache_path.parent):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path: Path = Path(args.mapping)
    if mapping_path.exists():
        try:
            main(mapping_path, cache_path, args.default_language, args.languages)
        except Exception as e:
            logger.error(e)
            import traceback
            traceback.print_exc()
