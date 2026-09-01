# -*- coding: utf-8 -*-
# Copyright © 2025-present Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language_code governing permissions and
#  limitations under the License.
"""
Scrape Wikidata into the Private Knowledge import format.

The script seeds a crawl either from a SPARQL query or from an explicit list of QIDs,
walks the object properties of every entity it pulls to discover further QIDs, maps the
result onto ``ThingObject`` instances via the ontology mapping configuration, and writes
an NDJSON file that ``samples/import_entities.py`` can push into a tenant.

No Private Knowledge credentials are required — the whole pipeline talks to Wikidata and
to the local mapping configuration only.

Configuration file (see ``scrapping/artwork.json`` for a ready-made example)::

    {"name": "artwork", "entity-list": ["Q762", "Q5582"]}

or, to discover the seeds with SPARQL::

    {
      "name": "painters",
      "query": {
        "filters": [{"property": "P31", "target": "Q5"}],
        "dynamic-filters": {"property": "P106", "targets": ["Q1028181"]},
        "limit": 1000,
        "language_code": "en"
      }
    }

Example::

    python samples/wikidata_scrapping.py -c scrapping/artwork.json -o ./out \
        --languages en de --max-depth 1 --wikipedia-summary --nel --full-text

Note on ontology registration
-----------------------------
The mapping configuration expands property domains and ranges over the ontology class
hierarchy. This sample only loads ``pkl-cache/ontology_mapping.json`` and does not call
``knowledge.ontomapping.register_ontology()`` with a tenant's RDF export, because that
needs credentials. Without it the subclass expansion is narrower, so a few properties
that would map for a registered ontology are reported as warnings instead.
"""

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from tqdm import tqdm

from knowledge import logger
from knowledge.base.language import LANGUAGE_LOCALE_MAPPING, LanguageCode, LocaleCode
from knowledge.base.ontology import ThingObject
from knowledge.ontomapping import (
    ClassConfiguration,
    PropertyConfiguration,
    PropertyType,
    get_mapping_configuration,
    load_configuration,
)
from knowledge.ontomapping.manager import wikidata_to_thing
from knowledge.public.cache import WikidataCache
from knowledge.public.client import WikiDataAPIClient
from knowledge.public.relations import wikidata_relations_extractor
from knowledge.public.wikidata import Claim, WikidataThing
from knowledge.utils.import_format import save_import_format

# --------------------------------------------------- Structures -------------------------------------------------------
SPARQL_QUERY_MODE: str = "query"
ENTITY_LIST_MODE: str = "entity-list"
NAME_TAG: str = "name"
WIKIBASE_ITEM_TYPE: str = "wikibase-item"
WIKI_SITE: str = "wiki"

DEFAULT_CACHE_PATH: Path = Path(__file__).parent.parent / "pkl-cache"
DEFAULT_MAPPING_PATH: Path = DEFAULT_CACHE_PATH / "ontology_mapping.json"


@dataclass
class ScrapOptions:
    """
    Options controlling what is crawled and how the mapped entities are indexed.

    Parameters
    ----------
    languages: List[str]
        Wikidata language codes to keep, e.g. ``["en", "de"]``. Mapped onto the SDK
        locales via ``LANGUAGE_LOCALE_MAPPING``; unsupported codes are dropped.
    max_depth: int
        Number of expansion hops beyond the seed entities. ``0`` scrapes the seeds only,
        ``-1`` crawls until no new QIDs are discovered.
    include_wikipedia_summary: bool
        Pull the Wikipedia summary into the entity description.
    enable_vector_search: bool
        Mark the mapped entities for the vector (semantic) label index.
    enable_nel_search: bool
        Mark the mapped entities for Named Entity Linking.
    enable_full_text_search: bool
        Mark the mapped entities for the full text index.
    """

    languages: List[str] = field(default_factory=lambda: ["en"])
    max_depth: int = -1
    include_wikipedia_summary: bool = False
    enable_vector_search: bool = False
    enable_nel_search: bool = False
    enable_full_text_search: bool = False

    def supported_locales(self) -> List[LocaleCode]:
        """
        Resolve the configured language codes to the locales the SDK supports.

        Returns
        -------
        locales: List[LocaleCode]
            Supported locales, in the order the languages were given.

        Raises
        ------
        ValueError
            If none of the configured languages is supported.
        """
        locales: List[LocaleCode] = [
            LANGUAGE_LOCALE_MAPPING[LanguageCode(la)]
            for la in self.languages
            if LanguageCode(la) in LANGUAGE_LOCALE_MAPPING
        ]
        if not locales:
            supported: str = ", ".join(sorted(LANGUAGE_LOCALE_MAPPING.keys()))
            raise ValueError(f"None of the languages {self.languages} is supported. Supported languages: {supported}.")
        return locales


# ------------------------------------------------ SPARQL query helpers ------------------------------------------------
def build_query(params: Dict[str, Any]) -> List[str]:
    """
    Build the SPARQL queries for a query configuration.

    A ``dynamic-filters`` block fans a single configuration out into one query per target,
    which keeps each query small enough for the public endpoint's timeout.

    Parameters
    ----------
    params: Dict[str, Any]
        Query configuration with ``filters``, optional ``dynamic-filters``, ``limit`` and
        ``language_code``.

    Returns
    -------
    queries: List[str]
        SPARQL query strings.
    """
    filters: List[Dict[str, Any]] = params.get("filters", [])
    dynamics: Optional[Dict[str, Any]] = params.get("dynamic-filters")
    limit: int = params.get("limit", 1000)
    lang_code: str = params.get("language_code", "en")
    filter_string: str = ""
    queries: List[str] = []
    for f in filters:
        filter_string += f"?item wdt:{f['property']}  wd:{f['target']}.\n"
    patterns: List[str] = [filter_string]
    if dynamics:
        property_str: str = dynamics["property"]
        patterns = [filter_string + f"?item wdt:{property_str}  wd:{target}.\n" for target in dynamics["targets"]]
    for pattern in patterns:
        queries.append(f"""SELECT DISTINCT ?item ?itemLabel WHERE {{
          {pattern}SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],{lang_code}". }}
        }}
        LIMIT {limit}
        """)
    return queries


def extract_qid(url: str) -> str:
    """
    Extract the QID from a Wikidata entity URL.

    Parameters
    ----------
    url: str
        Entity URL, e.g. ``http://www.wikidata.org/entity/Q762``.

    Returns
    -------
    qid: str
        The QID.
    """
    return url.split("/")[-1]


# --------------------------------------------------- Configuration ----------------------------------------------------
def load_scrapping_config(config_path: Path) -> Dict[str, Any]:
    """
    Load the scrapping configuration.

    Parameters
    ----------
    config_path: Path
        Path to the JSON configuration file.

    Returns
    -------
    config: Dict[str, Any]
        Configuration, with ``name`` defaulted to the file stem.

    Raises
    ------
    ValueError
        If the file does not exist or declares neither a query nor an entity list.
    """
    if not config_path.exists():
        raise ValueError(f"Scrapping configuration {config_path} not found.")
    with config_path.open("r", encoding="utf-8") as fp_config:
        config: Dict[str, Any] = json.load(fp_config)
    if SPARQL_QUERY_MODE not in config and ENTITY_LIST_MODE not in config:
        raise ValueError(
            f"Configuration {config_path} must define either '{SPARQL_QUERY_MODE}' or '{ENTITY_LIST_MODE}'."
        )
    config.setdefault(NAME_TAG, config_path.stem)
    return config


def seed_qids(config: Dict[str, Any]) -> Set[str]:
    """
    Determine the entry points of the crawl.

    Parameters
    ----------
    config: Dict[str, Any]
        Scrapping configuration.

    Returns
    -------
    qids: Set[str]
        Seed QIDs.
    """
    if SPARQL_QUERY_MODE in config:
        qids: Set[str] = set()
        for query in build_query(config[SPARQL_QUERY_MODE]):
            results: Dict[str, Any] = WikiDataAPIClient.sparql_query(query)
            qids.update(extract_qid(item["item"]["value"]) for item in results["results"]["bindings"])
        return qids
    return set(config[ENTITY_LIST_MODE])


# ------------------------------------------------------ Crawling ------------------------------------------------------
def referenced_qids(entity: WikidataThing, properties: List[PropertyConfiguration]) -> Set[str]:
    """
    Collect the QIDs an entity points at through the given object properties.

    Parameters
    ----------
    entity: WikidataThing
        Entity to inspect.
    properties: List[PropertyConfiguration]
        Object properties to follow.

    Returns
    -------
    qids: Set[str]
        Referenced QIDs.
    """
    qids: Set[str] = set()
    for prop in properties:
        for pid in prop.pids:
            claim: Optional[Claim] = entity.claims.get(pid)
            if claim is None:
                continue
            for literal in claim.literals:
                if isinstance(literal, dict) and literal.get("type") == WIKIBASE_ITEM_TYPE:
                    qids.add(literal["value"]["id"])
    return qids


def check_missing_qids(
    entities: List[WikidataThing],
    known_qids: Set[str],
    progress: Optional[Callable[[int, int], None]] = None,
) -> Set[str]:
    """
    Collect the QIDs referenced by the object properties of the given entities.

    Only properties the mapping configuration knows about are followed — that is what
    keeps the crawl from drifting into unrelated corners of Wikidata.

    Parameters
    ----------
    entities: List[WikidataThing]
        Entities to inspect.
    known_qids: Set[str]
        QIDs that have already been pulled.
    progress: Optional[Callable[[int, int], None]]
        Progress callback over the inspected entities.

    Returns
    -------
    missing: Set[str]
        QIDs referenced but not yet pulled.
    """
    missing: Set[str] = set()
    for ctr, entity in enumerate(entities, start=1):
        if progress:
            progress(ctr, len(entities))
        wiki_classes: List[str] = [cls.qid for cls in entity.instance_of]
        class_conf: Optional[ClassConfiguration] = get_mapping_configuration().guess_classed(wiki_classes)
        if class_conf is None:
            continue
        properties: List[PropertyConfiguration] = get_mapping_configuration().property_for(
            class_conf.concept_type, PropertyType.OBJECT_PROPERTY
        )
        missing.update(referenced_qids(entity, properties) - known_qids)
    return missing


def crawl_wikidata(
    seeds: Set[str],
    max_depth: int = -1,
    progress: Optional[Callable[[int, int], None]] = None,
) -> Dict[str, WikidataThing]:
    """
    Breadth-first crawl of Wikidata starting from the seed QIDs.

    ``WikiDataAPIClient.retrieve_entities`` consults the shared ``WikidataCache`` before
    hitting the network, so a warm cache turns a re-run into a local operation.

    Parameters
    ----------
    seeds: Set[str]
        Seed QIDs.
    max_depth: int
        Number of expansion hops beyond the seeds. ``0`` pulls the seeds only, ``-1``
        crawls until no new QIDs are discovered.
    progress: Optional[Callable[[int, int], None]]
        Progress callback over the pulled entities.

    Returns
    -------
    collected: Dict[str, WikidataThing]
        Pulled entities, keyed by QID.
    """
    collected: Dict[str, WikidataThing] = {}
    frontier: Set[str] = set(seeds)
    depth: int = 0
    while frontier:
        entities: List[WikidataThing] = WikiDataAPIClient.retrieve_entities(frontier)
        for entity in entities:
            collected[entity.qid] = entity
        if max_depth != -1 and depth >= max_depth:
            frontier = set()
        else:
            frontier = check_missing_qids(entities, set(collected.keys()))
        logger.info(f"Depth {depth}: {len(collected)} entities pulled, {len(frontier)} queued.")
        if progress:
            progress(len(collected), len(collected) + len(frontier))
        depth += 1
    return collected


# ------------------------------------------------------ Mapping -------------------------------------------------------
def cleanup_thing_object(thing: ThingObject, qid: str, locales: List[LocaleCode]) -> bool:
    """
    Drop labels, aliases and descriptions that are empty or in an unrequested locale.

    Two things make this necessary. Wikidata occasionally carries empty strings, and the
    service rejects an entity that has none of them left, so the caller must skip such an
    entity rather than import it. And ``wikidata_to_thing`` falls back to copying *every*
    Wikidata description when no Wikipedia summary was pulled, which can yield locales
    outside the requested set — and outside ``SUPPORTED_LOCALES`` entirely, in which case
    ``load_import_format`` refuses to read the file back.

    Parameters
    ----------
    thing: ThingObject
        Entity to clean up, modified in place.
    qid: str
        QID of the source entity, for logging.
    locales: List[LocaleCode]
        Locales to keep.

    Returns
    -------
    importable: bool
        True if the entity still has a label and a source reference id.
    """
    kept: Set[str] = {str(locale) for locale in locales}
    for attribute in ("label", "alias", "description"):
        values: List[Any] = getattr(thing, attribute)
        valid: List[Any] = [v for v in values if v.content and str(v.language_code) in kept]
        removed: int = len(values) - len(valid)
        if removed > 0:
            logger.debug(f"[QID: {qid}] Removed {removed} {attribute}(s): empty content or unrequested locale.")
            setattr(thing, attribute, valid)
    if len(thing.label) == 0:
        logger.warning(f"[QID: {qid}] Skipping entity - no valid labels after cleanup.")
        return False
    if not thing.default_source_reference_id():
        logger.warning(f"[QID: {qid}] Skipping entity - no valid source reference ID.")
        return False
    return True


def collect_warning(warning: Dict[str, Any], aggregated: Dict[str, Dict[str, Any]]) -> None:
    """
    Fold a single mapping warning into the per-property aggregate.

    Parameters
    ----------
    warning: Dict[str, Any]
        Warning produced by ``wikidata_to_thing``.
    aggregated: Dict[str, Dict[str, Any]]
        Aggregate keyed by PID, modified in place.
    """
    if "property" not in warning:
        return
    pid: str = warning["property"]
    entry: Dict[str, Any] = aggregated.setdefault(
        pid, {"property": pid, "source_qids": [], "target_qids": [], "source_classes": [], "target_classes": []}
    )
    for key, values in (
        ("source_classes", warning.get("source_classes", [])),
        ("target_classes", warning.get("target_classes", [])),
        ("source_qids", [warning.get("source_qid")]),
        ("target_qids", [warning.get("target_qid")]),
    ):
        for value in values:
            if value is not None and value not in entry[key]:
                entry[key].append(value)


def map_to_things(
    wikidata_things: Dict[str, WikidataThing],
    relations: Dict[str, List[Dict[str, Any]]],
    options: ScrapOptions,
    progress: Optional[Callable[[int, int], None]] = None,
) -> Tuple[List[ThingObject], Dict[str, Dict[str, Any]]]:
    """
    Map the crawled Wikidata entities onto ThingObjects.

    Parameters
    ----------
    wikidata_things: Dict[str, WikidataThing]
        Crawled entities, keyed by QID.
    relations: Dict[str, List[Dict[str, Any]]]
        Relations extracted from the crawled entities.
    options: ScrapOptions
        Language and indexing options.
    progress: Optional[Callable[[int, int], None]]
        Progress callback over the mapped entities.

    Returns
    -------
    things: List[ThingObject]
        Entities ready for import.
    warnings: Dict[str, Dict[str, Any]]
        Mapping warnings, aggregated per property.
    """
    locales: List[LocaleCode] = options.supported_locales()
    things: List[ThingObject] = []
    warnings: Dict[str, Dict[str, Any]] = {}
    for ctr, w_thing in enumerate(wikidata_things.values(), start=1):
        if progress:
            progress(ctr, len(wikidata_things))
        try:
            thing, import_warnings = wikidata_to_thing(
                w_thing,
                relations,
                list(locales),
                wikidata_things,
                pull_wikipedia=options.include_wikipedia_summary,
            )
        except ValueError as ve:
            logger.error(f"Importing Wikidata entity {w_thing.qid} failed: {ve}")
            continue
        if not cleanup_thing_object(thing, w_thing.qid, locales):
            continue
        thing.use_vector_index = options.enable_vector_search
        thing.use_for_nel = options.enable_nel_search
        thing.use_full_text_index = options.enable_full_text_search
        things.append(thing)
        for warning in import_warnings:
            collect_warning(warning, warnings)
    return things, warnings


# --------------------------------------------------- Orchestration ----------------------------------------------------
def scrap_wikidata(
    scrapping_config: Dict[str, Any],
    output_path: Path,
    options: ScrapOptions,
    cache_path: Path = DEFAULT_CACHE_PATH,
    mapping_path: Path = DEFAULT_MAPPING_PATH,
    progress_wikidata: Optional[Callable[[int, int], None]] = None,
    progress_relations: Optional[Callable[[int, int], None]] = None,
    progress_mapping: Optional[Callable[[int, int], None]] = None,
) -> Path:
    """
    Run the full crawl, map and write pipeline.

    Parameters
    ----------
    scrapping_config: Dict[str, Any]
        Scrapping configuration, as returned by ``load_scrapping_config``.
    output_path: Path
        Directory the NDJSON and the warnings report are written to.
    options: ScrapOptions
        Crawl depth, languages and indexing options.
    cache_path: Path
        Directory holding the Wikidata cache. (Default: ``pkl-cache``)
    mapping_path: Path
        Ontology mapping configuration. (Default: ``pkl-cache/ontology_mapping.json``)
    progress_wikidata: Optional[Callable[[int, int], None]]
        Progress callback for the crawl.
    progress_relations: Optional[Callable[[int, int], None]]
        Progress callback for the relation extraction.
    progress_mapping: Optional[Callable[[int, int], None]]
        Progress callback for the mapping.

    Returns
    -------
    thing_path: Path
        Path of the written NDJSON import file.
    """
    name: str = scrapping_config[NAME_TAG]
    output_path.mkdir(parents=True, exist_ok=True)
    load_configuration(mapping_path)
    cache: WikidataCache = WikidataCache()
    cache.load_cache(cache_path)

    seeds: Set[str] = seed_qids(scrapping_config)
    logger.info(f"Scrapping '{name}' from {len(seeds)} seed entities (max depth: {options.max_depth}).")
    wikidata_things: Dict[str, WikidataThing] = crawl_wikidata(seeds, options.max_depth, progress_wikidata)
    cache.save_cache(cache_path)

    relations: Dict[str, List[Dict[str, Any]]] = wikidata_relations_extractor(wikidata_things, progress_relations)
    things, warnings = map_to_things(wikidata_things, relations, options, progress_mapping)

    thing_path: Path = output_path / f"{name}_{options.max_depth}.ndjson"
    save_import_format(thing_path, things)
    warnings_path: Path = output_path / f"{name}_warnings.json"
    with warnings_path.open("w", encoding="utf-8") as fp_warnings:
        json.dump(warnings, fp_warnings, ensure_ascii=False)
    logger.info(f"Wrote {len(things)} entities to {thing_path} ({len(warnings)} properties with warnings).")
    return thing_path


class TqdmProgress:
    """
    Lazily created tqdm bar wired to the SDK's ``Callable[[int, int], None]`` signature.

    The bar is only created on the first callback, because the totals are not known until
    the first batch has been processed, and it is resized whenever the total grows.

    Parameters
    ----------
    desc: str
        Description shown in front of the bar.
    unit: str
        Unit shown behind the counter.
    """

    def __init__(self, desc: str, unit: str = "entity") -> None:
        self.__desc: str = desc
        self.__unit: str = unit
        self.__bar: Optional[tqdm] = None

    def __call__(self, completed: int, total: int) -> None:
        if self.__bar is None:
            self.__bar = tqdm(total=total, desc=self.__desc, unit=self.__unit)
        if total != self.__bar.total:
            self.__bar.total = total
            self.__bar.refresh()
        delta: int = completed - self.__bar.n
        if delta > 0:
            self.__bar.update(delta)

    def close(self) -> None:
        """Close the bar, if it was ever created."""
        if self.__bar is not None:
            self.__bar.close()
            self.__bar = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Wikidata into the Private Knowledge import format.")
    parser.add_argument("-c", "--config", help="Path to the scrapping configuration.", required=True, type=Path)
    parser.add_argument("-o", "--output", help="Directory for the generated files.", required=True, type=Path)
    parser.add_argument("-l", "--languages", nargs="+", default=["en"], help="Wikidata language codes to keep.")
    parser.add_argument("-d", "--max-depth", type=int, default=-1, help="Expansion hops beyond the seeds (-1: all).")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE_PATH, help="Directory of the Wikidata cache.")
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING_PATH, help="Ontology mapping configuration.")
    parser.add_argument("--wikipedia-summary", action="store_true", help="Pull Wikipedia summaries as descriptions.")
    parser.add_argument("--vector-search", action="store_true", help="Index the entities for vector search.")
    parser.add_argument("--nel", action="store_true", help="Index the entities for Named Entity Linking.")
    parser.add_argument("--full-text", action="store_true", help="Index the entities for full text search.")
    args = parser.parse_args()

    scrap_options: ScrapOptions = ScrapOptions(
        languages=args.languages,
        max_depth=args.max_depth,
        include_wikipedia_summary=args.wikipedia_summary,
        enable_vector_search=args.vector_search,
        enable_nel_search=args.nel,
        enable_full_text_search=args.full_text,
    )
    wikidata_bar: TqdmProgress = TqdmProgress("Crawling Wikidata")
    relations_bar: TqdmProgress = TqdmProgress("Extracting relations")
    mapping_bar: TqdmProgress = TqdmProgress("Mapping entities")
    try:
        scrap_wikidata(
            load_scrapping_config(args.config),
            args.output,
            scrap_options,
            cache_path=args.cache,
            mapping_path=args.mapping,
            progress_wikidata=wikidata_bar,
            progress_relations=relations_bar,
            progress_mapping=mapping_bar,
        )
    finally:
        wikidata_bar.close()
        relations_bar.close()
        mapping_bar.close()
