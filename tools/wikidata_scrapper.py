# -*- coding: utf-8 -*-
# Copyright © 2023-24 Wacom. All rights reserved.
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Any, Dict, List, Set

import ndjson
from tqdm import tqdm

from knowledge import logger
from knowledge.base.entity import LanguageCode, IMAGE_TAG, STATUS_FLAG_TAG, Description, Label
from knowledge.base.language import LANGUAGE_LOCALE_MAPPING, LocaleCode
from knowledge.base.ontology import ThingObject, OntologyContext, OntologyClassReference
from knowledge.ontomapping import get_mapping_configuration, register_ontology, PropertyConfiguration, PropertyType, \
    load_configuration, ClassConfiguration
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


# ----------------------------------------------- Helper functions -----------------------------------------------------
def update_language_code(lang: LanguageCode) -> LocaleCode:
    """ Update the language_code code to a default language_code / country code
    Parameters
    ----------
    lang: LanguageCode
        Language code.

    Returns
    -------
    language_code: LocaleCode
        Language code.

    Raises
    ------
    ValueError
        If the language_code code is not supported.
    """
    if lang not in LANGUAGE_LOCALE_MAPPING:
        raise ValueError(f'Language code {lang} not supported.')
    return LANGUAGE_LOCALE_MAPPING[lang]


def localized_list_description(entity_dict: Dict[str, str]) -> List[Description]:
    """
    Creates a list of descriptions for the given entity dictionary.
    Parameters
    ----------
    entity_dict: Dict[str, str]
        Entity dictionary.

    Returns
    -------
    descriptions: List[Description]
        List of descriptions.
    """
    return [Description(cont, update_language_code(LanguageCode(lang))) for lang, cont in entity_dict.items()]


def localized_list_label(entity_dict: Dict[str, str]) -> List[Label]:
    """
    Creates a list of labels for the given entity dictionary.

    Parameters
    ----------
    entity_dict: Dict[str, str]
        Entity dictionary.

    Returns
    -------
    labels: List[Label]
        List of labels.
    """
    return [Label(cont, update_language_code(LanguageCode(lang)), main=True)
            for lang, cont in entity_dict.items() if cont != '']


def localized_flatten_alias_list(entity_dict: Dict[str, List[str]]) -> List[Label]:
    """
    Flattens the alias list.
    Parameters
    ----------
    entity_dict: Dict[str, List[str]]
        Entity dictionary.

    Returns
    -------
    flatten: List[Label]
        Flattened list of labels.
    """
    flatten: List[Label] = []
    for language, items in entity_dict.items():
        for i in items:
            if i != '':
                flatten.append(Label(i, update_language_code(LanguageCode(language)), main=False))
    return flatten


def from_dict(entity: Dict[str, Any], concept_type: OntologyClassReference) -> ThingObject:
    """
    Create a thing object from a dictionary.
    Parameters
    ----------
    entity: Dict[str, Any]
        Entity dictionary.
    concept_type: OntologyClassReference
        Concept type.

    Returns
    -------
    thing: ThingObject
        Thing object.
    """
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
        filter_string += f"?item wdt:{f['property']}  wd:{f['target']}.\n"
    if dynamics:
        property_str: str = dynamics["property"]
        for v in dynamics["targets"]:
            dyn: str = filter_string + f"?item wdt:{property_str}  wd:{v}.\n"
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


def load_cache(cache: Path) -> Dict[str, WikidataThing]:
    """
    Load the cache from the file.
    Parameters
    ----------
    cache: Path
        The path to the cache file.

    Returns
    -------
    wikidata_things: Dict[str, WikidataThing]
        Dictionary of Wikidata things.
    """
    wikidata_things: Dict[str, WikidataThing] = {}
    if cache.exists():
        with cache.open('r') as r:
            reader = ndjson.reader(r)
            for line in reader:
                wikidata_things[line['qid']] = WikidataThing.create_from_dict(line)
    return wikidata_things


def count_type(concept_type: str, types_mapping: Dict[str, int]):
    """
    Count the number of types.
    Parameters
    ----------
    concept_type: str
        Concept type.
    types_mapping: Dict[str, int]
        Dictionary of types.
    """
    if concept_type not in types_mapping:
        types_mapping[concept_type] = 0
    types_mapping[concept_type] += 1


def check_missing_qids(entities: List[WikidataThing]) -> Set[str]:
    """
    Check if there are missing qids in the retrieved entities.
    Parameters
    ----------
    entities: List[WikidataThing]
        List of entities.

    Returns
    -------
    missing: Set[str]
        Set of missing qids.
    """
    missing: Set[str] = set()
    for entity in tqdm(entities, desc="Checking missing qid references."):
        wiki_classes: Set[str] = set()
        for cls in entity.instance_of:
            hierarchy: WikidataClass = wikidata_taxonomy(cls.qid)
            if hierarchy:
                wiki_classes.update([c.qid for c in hierarchy.superclasses])
                wiki_classes.add(hierarchy.qid)
        class_conf: Optional[ClassConfiguration] = get_mapping_configuration().guess_classed(list(wiki_classes))
        if class_conf:
            properties: List[PropertyConfiguration] = get_mapping_configuration(). \
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
    parts: List[str] = url.split('/')
    return parts[-1]


def main(mapping: Path, cache: Path, languages: List[str] = None, max_depth: int = -1):
    """
    Main.

    Arguments
    ---------
    mapping: Path
        The path to mapping file
    cache: Path
        The path to cache file with ThingObjects
    languages: List[str]
        List of languages
    max_depth: int
        Maximum depth of the crawling
    """
    # All failed jobs
    cache.mkdir(parents=True, exist_ok=True)
    wikidata_path: Path = cache / 'wikidata.ndjson'
    thing_path: Path = cache / 'things.ndjson'
    warnings_path: Path = cache / 'warnings.json'

    all_wikidata_things: Dict[str, WikidataThing] = load_cache(wikidata_path)
    # Load mapping
    with mapping.open('r') as json_file:
        configuration: Dict[str, Any] = json.load(json_file)

    imported_qids: Set[str] = set()
    if thing_path.exists():
        with thing_path.open('r') as r:
            reader = ndjson.reader(r)
            for line in reader:
                thing: ThingObject = ThingObject.from_import_dict(line)
                imported_qids.add(thing.reference_id)

    # List of qids
    qid_references: Set[str] = set()

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
        entities: List[WikidataThing] = []
        qids_to_remove: Set[str] = set()
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
            pull_entities: List[WikidataThing] = WikiDataAPIClient.retrieve_entities(qid_references)
        else:
            pull_entities: List[WikidataThing] = []
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
        depth += 1
    relations: Dict[str, List[Dict[str, Any]]] = wikidata_relations_extractor(all_wikidata_things)
    logger.info(f"{len(all_wikidata_things)} entities are imported.")

    thing_objects: List[ThingObject] = []
    # process warnings
    import_warnings_property: Dict[str, Dict[str, Any]] = {}
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
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance")
    parser.add_argument("-o", "--output", type=Path, help="Path to output directory.")
    parser.add_argument("-m", "--mapping", type=Path, help="Ontology mappings.")
    parser.add_argument("-d", "--depth", help="Depth of crawling, if -1 depth it is infinite.", default=4,
                        type=int)
    parser.add_argument("-l", "--languages", nargs='+', default=['en'],
                        help="List of languages to import")
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
        load_configuration(Path('pkl-cache/ontology_mapping.json'))
    # ------------------------------------------------------------------------------------------------------------------
    cache_path: Path = Path(args.output)
    if not os.path.exists(cache_path.parent):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path: Path = Path(args.mapping)
    if mapping_path.exists():
        main(mapping_path, cache_path, args.languages, max_depth=args.depth)
