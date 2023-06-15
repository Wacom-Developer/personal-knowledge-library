# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Any

import ndjson
from tqdm import tqdm

from knowledge import logger
from knowledge.base.entity import LanguageCode, IMAGE_TAG, STATUS_FLAG_TAG, Description, Label
from knowledge.base.ontology import ThingObject, OntologyContext, OntologyClassReference, LANGUAGE_LOCALE_MAPPING
from knowledge.ontomapping import get_mapping_configuration, register_ontology, PropertyConfiguration, PropertyType, \
    update_taxonomy_cache, load_configuration
from knowledge.ontomapping.manager import wikidata_to_thing, wikidata_taxonomy
from knowledge.public.relations import wikidata_relations_extractor
from knowledge.public.wikidata import WikiDataAPIClient, WikidataThing, WikidataClass
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService


# -------------------------------------------------- Structures --------------------------------------------------------
class WikidataSyncException(Exception):
    """
    Exception class for Wikidata synchronization.
    """


# -------------------------------------------------- Structures --------------------------------------------------------
WACOM_KNOWLEDGE_TAG: str = 'wacom-knowledge'
ICON_TAG: str = 'icon'
DEFAULT_TYPE_TAG: str = "default-type"
ENTITY_LIST_MODE: str = 'entity-list'
SPARQL_QUERY_MODE: str = 'query'
CLASS_MAPPING: str = 'class-mapping'

# Mapping to map the simple language_code code to a default language_code / country code
language_code_mapping: dict[str, LanguageCode] = {
    'en': LanguageCode('en_US'),
    'ja': LanguageCode('ja_JP'),
    'de': LanguageCode('de_DE'),
    'bg': LanguageCode('bg_BG'),
    'zh': LanguageCode('zh_CN'),
    'fr': LanguageCode('fr_FR'),
    'it': LanguageCode('it_IT')
}


# ----------------------------------------------- Helper functions -----------------------------------------------------
def update_language_code(lang: str) -> LanguageCode:
    """ Update the language_code code to a default language_code / country code
    Parameters
    ----------
    lang: str
        Language code.

    Returns
    -------
    language_code: LanguageCode
        Language code.

    Raises
    ------
    ValueError
        If the language_code code is not supported.
    """
    if lang not in language_code_mapping:
        raise ValueError(f'Language code {lang} not supported.')
    return language_code_mapping[lang]


def localized_list_description(entity_dict: dict[str, str]) -> list[Description]:
    """
    Creates a list of descriptions for the given entity dictionary.
    Parameters
    ----------
    entity_dict: dict[str, str]
        Entity dictionary.

    Returns
    -------
    descriptions: list[Description]
        List of descriptions.
    """
    return [Description(cont, update_language_code(lang)) for lang, cont in entity_dict.items()]


def localized_list_label(entity_dict: dict[str, str]) -> list[Label]:
    """
    Creates a list of labels for the given entity dictionary.

    Parameters
    ----------
    entity_dict: dict[str, str]
        Entity dictionary.

    Returns
    -------
    labels: list[Label]
        List of labels.
    """
    return [Label(cont, update_language_code(lang), main=True) for lang, cont in entity_dict.items() if cont != '']


def localized_flatten_alias_list(entity_dict: dict[str, list[str]]) -> list[Label]:
    """
    Flattens the alias list.
    Parameters
    ----------
    entity_dict: dict[str, list[str]]
        Entity dictionary.

    Returns
    -------
    flatten: list[Label]
        Flattened list of labels.
    """
    flatten: list[Label] = []
    for language, items in entity_dict.items():
        for i in items:
            if i != '':
                flatten.append(Label(i, update_language_code(language), main=False))
    return flatten


def from_dict(entity: dict[str, Any], concept_type: OntologyClassReference) -> ThingObject:
    """
    Create a thing object from a dictionary.
    Parameters
    ----------
    entity: dict[str, Any]
        Entity dictionary.
    concept_type: OntologyClassReference
        Concept type.

    Returns
    -------
    thing: ThingObject
        Thing object.
    """
    labels: list[Label] = localized_list_label(entity['label'])
    description: list[Description] = localized_list_description(entity['description'])
    alias: list[Label] = localized_flatten_alias_list(entity['alias'])
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
    Parameters
    ----------
    url: str
        URL
    Returns
    -------
    result: str
        Stripped URL
    """
    parts = url.split('/')
    return parts[-1]


def build_query(params: dict[str, Any]) -> list[str]:
    """
    Build of query.

    Parameters
    ----------
    params:
        Parameters for query

    Returns
    -------
    queries: list[str]
        SPARQL query string
    """
    filters: list[dict[str, Any]] = params.get('filters')
    dynamics: dict[str, Any] = params.get('dynamic-filters')
    limit: int = params.get('limit', 1000)
    lang_code: str = params.get('language_code', 'en')
    filter_string: str = ''
    queries: list[str] = []
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


def load_cache(cache: Path) -> dict[str, WikidataThing]:
    """
    Load the cache from the file.
    Parameters
    ----------
    cache: Path
        Path to the cache file.

    Returns
    -------
    wikidata_things: dict[str, WikidataThing]
        Dictionary of Wikidata things.
    """
    wikidata_things: dict[str, WikidataThing] = {}
    if cache.exists():
        with cache.open('r') as r:
            reader = ndjson.reader(r)
            for line in reader:
                wikidata_things[line['qid']] = WikidataThing.create_from_dict(line)
    return wikidata_things


def count_type(concept_type: str, types_mapping: dict[str, int]):
    """
    Count the number of types.
    Parameters
    ----------
    concept_type: str
        Concept type.
    types_mapping: dict[str, int]
        Dictionary of types.
    """
    if concept_type not in types_mapping:
        types_mapping[concept_type] = 0
    types_mapping[concept_type] += 1


def check_missing_qids(entities: list[WikidataThing]) -> set[str]:
    """
    Check if there are missing qids in the retrieved entities.
    Parameters
    ----------
    entities: list[WikidataThing]
        List of entities.

    Returns
    -------
    missing: set[str]
        Set of missing qids.
    """
    missing: set[str] = set()
    for entity in tqdm(entities, desc="Checking missing qid references."):
        wiki_classes: set[str] = set()
        for cls in entity.instance_of:
            hierarchy: WikidataClass = wikidata_taxonomy(cls.qid)
            if hierarchy:
                wiki_classes.update([c.qid for c in hierarchy.superclasses])
                wiki_classes.add(hierarchy.qid)
        class_conf = get_mapping_configuration().guess_classed(list(wiki_classes))
        if class_conf:
            properties: list[PropertyConfiguration] = get_mapping_configuration(). \
                property_for(class_conf.concept_type, PropertyType.OBJECT_PROPERTY)
            for prop in properties:
                for pid in prop.pids:
                    if pid in entity.claims:
                        for cl in entity.claims[pid].literals:
                            if isinstance(cl, dict) and cl['type'] == "wikibase-item":
                                qid: str = cl['value']['id']
                                missing.add(qid)
    return missing


def extract_qid(url: str) -> str:
    """
    Extract qid from url.
    Parameters
    ----------
    url: str
        URL

    Returns
    -------
    qid: str
        QID
    """
    parts: list[str] = url.split('/')
    return parts[-1]


def main(mapping: Path, cache: Path, languages: list[str] = None, max_depth: int = -1):
    """
    Main.

    Arguments
    ---------
    mapping: Path
        Path to mapping file
    cache: Path
        Path to cache file with ThingObjects
    languages: list[str]
        List of languages
    max_depth: int
        Maximum depth of the crawling
    """
    # All failed jobs
    cache.mkdir(parents=True, exist_ok=True)
    wikidata_path: Path = cache / 'wikidata.ndjson'
    thing_path: Path = cache / 'things.ndjson'
    warnings_path: Path = cache / 'warnings.json'

    all_wikidata_things: dict[str, WikidataThing] = load_cache(wikidata_path)
    # Load mapping
    with mapping.open('r') as json_file:
        configuration: dict[str, Any] = json.load(json_file)

    imported_qids: set[str] = set()
    if thing_path.exists():
        with thing_path.open('r') as r:
            reader = ndjson.reader(r)
            for line in reader:
                thing: ThingObject = ThingObject.from_import_dict(line)
                imported_qids.add(thing.reference_id)

    # List of qids
    qid_references: set[str] = set()

    # First query the entry entities
    if SPARQL_QUERY_MODE in configuration:
        queries: list = build_query(configuration[SPARQL_QUERY_MODE])
        for query in queries:
            results: dict = WikiDataAPIClient.sparql_query(query)
            qid_references.update([extract_qid(item['item']['value']) for item in results['results']['bindings']])
    # Or use a list of qids
    elif ENTITY_LIST_MODE in configuration:
        qid_references = set(configuration[ENTITY_LIST_MODE])
    else:
        logger.error("No jobs defined.")
        sys.exit(0)
    depth: int = 0
    while len(qid_references) > 0 and (depth == -1 or depth < max_depth):
        entities: list[WikidataThing] = []
        qids_to_remove: set[str] = set()
        # Check for existing entities
        for ref_qid in qid_references:
            if ref_qid in all_wikidata_things:
                qids_to_remove.add(ref_qid)
                entities.append(all_wikidata_things[ref_qid])
        # Remove cached entities
        for item in qids_to_remove:
            qid_references.remove(item)
        # Retrieve entities
        if len(qid_references) > 0:
            pull_entities: list[WikidataThing] = WikiDataAPIClient.retrieve_entities(qid_references)
        else:
            pull_entities: list[WikidataThing] = []
        # Merge entities
        entities.extend(pull_entities)
        # Cache entities
        for entity in pull_entities:
            all_wikidata_things[entity.qid] = entity
        # Save cache
        with wikidata_path.open('w') as fp:
            for entity in pull_entities:
                fp.write(f"{json.dumps(entity.__dict__(), ensure_ascii=False)}\n")
        # Check for missing qids
        qid_references = check_missing_qids(entities)
        logger.info(f"Retrieved {len(all_wikidata_things)} entities. Cache for {len(qid_references)} entities. "
                    f"Depth {depth} (max {max_depth}).")
        # Cache more taxonomy
        update_taxonomy_cache()
        depth += 1
    relations: dict[str, list[dict[str, Any]]] = wikidata_relations_extractor(all_wikidata_things)
    logger.info(f"{len(all_wikidata_things)} entities are imported.")

    thing_objects: list[ThingObject] = []
    # process warnings
    import_warnings_property: dict[str, dict[str, Any]] = {}
    with thing_path.open('w', encoding='utf-8') as fp_thing:
        for _, w_thing in tqdm(all_wikidata_things.items(),
                               desc=f"Processing {len(all_wikidata_things)} Wikidata entities."):
            thing, import_warnings = wikidata_to_thing(w_thing, relations,
                                                       [LANGUAGE_LOCALE_MAPPING[la] for la in languages
                                                        if la in LANGUAGE_LOCALE_MAPPING], all_wikidata_things,
                                                       pull_wikipedia=True)
            thing_objects.append(thing)
            fp_thing.write(f"{json.dumps(thing.__import_format_dict__(), ensure_ascii=False)}\n")

            for warning in import_warnings:
                pid: str = warning['property']
                if warning['property'] not in import_warnings_property:
                    import_warnings_property[pid] = {
                        'label': warning['property_label'],
                        'property': pid,
                        'source_qids': [],
                        'target_qids': [],
                        'source_classes': [],
                        'target_classes': [],
                    }
                for source_class in warning['source_classes']:
                    if source_class not in import_warnings_property[pid]['source_classes']:
                        import_warnings_property[pid]['source_classes'].append(source_class)
                for target_class in warning['target_classes']:
                    if target_class not in import_warnings_property[pid]['target_classes']:
                        import_warnings_property[pid]['target_classes'].append(target_class)

                if warning['source_qid'] not in import_warnings_property[pid]['source_qids']:
                    import_warnings_property[pid]['source_qids'].append(warning['source_qid'])
                if warning['target_qid'] not in import_warnings_property[pid]['target_qids']:
                    import_warnings_property[pid]['target_qids'].append(warning['target_qid'])
    with warnings_path.open('w', encoding='utf-8') as fp:
        fp.write(f"{json.dumps(import_warnings_property, ensure_ascii=False)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default='https://stage-private-knowledge.wacom.com',
                        help="URL of instance")
    parser.add_argument("-c", "--cache", help="Path to output directory.")
    parser.add_argument("-m", "--mapping", help="Ontology mappings.")
    parser.add_argument("-d", "--depth", help="Depth of crawling, if -1 depth it is infinite.", default=4, type=int)
    parser.add_argument("-l", "--languages", nargs='+', default=['en'], help="List of languages to import")
    args = parser.parse_args()
    # Configure the ontology for tenant
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(service_url=args.instance,
                                                                    application_name="Ontology")
    ontology_client: OntologyService = OntologyService(service_url=args.instance)
    admin_token, refresh, expire = knowledge_client.request_user_token(args.tenant, args.user)
    context: Optional[OntologyContext] = ontology_client.context(admin_token)
    if not context:
        sys.exit(0)
    else:
        context_name: str = context.context
        # Export ontology
        rdf_export: str = ontology_client.rdf_export(admin_token, context_name)
        # Register ontology
        register_ontology(rdf_export)
        # Load configuration
        load_configuration()
    # ------------------------------------------------------------------------------------------------------------------
    cache_path: Path = Path(args.cache)
    if not os.path.exists(cache_path.parent):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path: Path = Path(args.mapping)
    if mapping_path.exists():
        main(mapping_path, cache_path, args.languages, max_depth=args.depth)

