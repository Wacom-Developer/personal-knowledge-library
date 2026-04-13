# -*- coding: utf-8 -*-
# Copyright © 2023-present Wacom. All rights reserved.
import multiprocessing
from collections import deque
from functools import lru_cache
from multiprocessing import Pool
from typing import Union, Any, Dict, List, Tuple, Set, Optional, Callable

import requests
from requests import Response, HTTPError
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from knowledge import logger, __version__
from knowledge.base.entity import (
    LanguageCode,
)
from knowledge.public.cache import WikidataCache
from knowledge.public.helper import (
    __waiting_request__,
    __waiting_multi_request__,
    WikiDataAPIException,
    WIKIDATA_SPARQL_URL,
    WIKIDATA_SEARCH_URL,
    API_LIMIT,
)
from knowledge.public.wikidata import (
    WikidataClass,
    WikidataThing,
    WikidataSearchResult,
    WikidataProperty,
)
from knowledge.services import USER_AGENT_HEADER_FLAG, DEFAULT_TIMEOUT

__all__ = [
    "QUALIFIERS_TAG",
    "LITERALS_TAG",
    "wikidata_cache",
    "chunks",
    "WikiDataAPIClient",
]

# Constants
QUALIFIERS_TAG: str = "QUALIFIERS"
LITERALS_TAG: str = "LITERALS"
# Cache for wikidata objects
wikidata_cache: WikidataCache = WikidataCache()

# Persistent session for Wikidata APIs (SPARQL + search) — reuses TCP connections
# Increased retries and added connection errors for Wikidata endpoint resilience
_retry_policy: Retry = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    respect_retry_after_header=True,
    raise_on_status=False,
)
_wikidata_session: requests.Session = requests.Session()
_wikidata_session.mount(
    "https://",
    HTTPAdapter(
        max_retries=_retry_policy,
        pool_connections=10,
        pool_maxsize=10,
    ),
)
_wikidata_session.mount(
    "http://",
    HTTPAdapter(
        max_retries=_retry_policy,
        pool_connections=10,
        pool_maxsize=10,
    ),
)


def chunks(lst: List[str], chunk_size: int):
    """
    Yield successive n-sized chunks from lst.Yield successive n-sized chunks from lst.
    Parameters
    ----------
    lst: List[str]
        Full length.
    chunk_size: int
        Chunk size.

    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


class WikiDataAPIClient:
    """
    Client for performing operations on Wikidata.

    This class provides methods to query Wikidata using SPARQL, retrieve superclasses
    and subclasses for a given Wikidata entity, and search for terms in Wikidata.
    It is intended to serve as a convenience interface for interacting with the Wikidata
    API and working with entity relationships.

    Methods
    -------
    sparql_query(query_string: str, wikidata_sparql_url: str = WIKIDATA_SPARQL_URL, max_retries: int = 3)
        Send a SPARQL query and return the JSON-formatted result.

    superclasses(qid: str) -> Dict[str, WikidataClass]
        Returns the Wikidata class and its superclasses for a given QID.

    subclasses(qid: str) -> Dict[str, WikidataClass]
        Returns the Wikidata class and its subclasses for a given QID.

    search_term(search_term: str, language: LanguageCode, url: str = WIKIDATA_SEARCH_URL) -> List[WikidataSearchResult]
        Search for a term in Wikidata.
    """

    def __init__(self):
        pass

    @staticmethod
    def headers() -> Dict[str, str]:
        """Return standard headers for Wikidata API requests."""
        return {
            USER_AGENT_HEADER_FLAG: (
                f"Personal Knowledge Library(WikiDataAPIClient)/{__version__}"
                f"(+https://github.com/Wacom-Developer/personal-knowledge-library)"
            )
        }

    @staticmethod
    def sparql_query(
        query_string: str,
        wikidata_sparql_url: str = WIKIDATA_SPARQL_URL,
        max_retries: int = 3,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> dict:
        """Send a SPARQL query and return the JSON-formatted result.

        Parameters
        -----------
        query_string: str
          SPARQL query string
        wikidata_sparql_url: str
          Wikidata SPARQL endpoint to use
        max_retries: int
            Maximum number of retries
        timeout: int
            Default timeout.
        """
        headers: Dict[str, str] = WikiDataAPIClient.headers()
        # Use persistent session for connection reuse
        try:
            response: Response = _wikidata_session.get(
                wikidata_sparql_url,
                params={"query": query_string, "format": "json"},
                timeout=timeout,
                headers=headers,
            )
            if response.ok:
                return response.json()
            raise WikiDataAPIException(
                f"Failed to query entities. "
                f"Response code:={response.status_code}, Exception:= {response.content}."
            )
        except requests.exceptions.JSONDecodeError as e:
            logger.warning(f"SPARQL query returned malformed JSON, retrying: {e}")
            raise

    @staticmethod
    def superclasses(qid: str) -> Dict[str, WikidataClass]:
        """
        Returns the Wikidata class with all its superclasses for the given QID.

        Parameters
        ----------
        qid: str
            Wikidata QID (e.g., 'Q146' for house cat).

        Returns
        -------
        classes: Dict[str, WikidataClass]
            A dictionary of WikidataClass objects, where the keys are QIDs and the values are the corresponding
        """
        # Fetch superclasses
        query = f"""
        SELECT DISTINCT ?class ?classLabel ?superclass ?superclassLabel
        WHERE
        {{
            wd:{qid} wdt:P279* ?class.
            ?class wdt:P279 ?superclass.
            SERVICE wikibase:label {{bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        """
        try:
            reply: Dict[str, Any] = WikiDataAPIClient.sparql_query(query)
            wikidata_classes: Dict[str, WikidataClass] = {}
            cycle_detector: Set[Tuple[str, str]] = set()
            adjacency_list: Dict[str, Set[str]] = {}

            if "results" in reply:
                for b in reply["results"]["bindings"]:
                    superclass_qid = b["superclass"]["value"].rsplit("/", 1)[-1]
                    class_qid = b["class"]["value"].rsplit("/", 1)[-1]
                    superclass_label = b["superclassLabel"]["value"]
                    class_label = b["classLabel"]["value"]
                    wikidata_classes.setdefault(
                        class_qid, WikidataClass(class_qid, class_label)
                    )
                    wikidata_classes.setdefault(
                        superclass_qid, WikidataClass(superclass_qid, superclass_label)
                    )
                    adjacency_list.setdefault(class_qid, set()).add(superclass_qid)
        except (ValueError, KeyError, HTTPError) as e:
            logger.exception(e)
            return {qid: WikidataClass(qid, f"Class {qid}")}
        queue = deque([qid])
        visited = set()

        while queue:
            current_qid = queue.popleft()
            if current_qid in visited:
                continue
            visited.add(current_qid)

            if current_qid in adjacency_list:
                for superclass_qid in adjacency_list[current_qid]:
                    if (current_qid, superclass_qid) not in cycle_detector:
                        wikidata_classes[current_qid].superclasses.append(
                            wikidata_classes[superclass_qid]
                        )
                        queue.append(superclass_qid)
                        cycle_detector.add((current_qid, superclass_qid))

        return wikidata_classes

    @staticmethod
    def subclasses(qid: str) -> Dict[str, WikidataClass]:
        """
        Returns the Wikidata class with all its subclasses for the given QID.

        Parameters
        ----------
        qid: str
            Wikidata QID (e.g., 'Q146' for house cat).

        Returns
        -------
        classes: Dict[str, WikidataClass]
            A dictionary of WikidataClass objects, where the keys are QIDs and the values are the corresponding
            classes with their subclasses populated.
        """
        try:
            results = WikiDataAPIClient._subclasses_cached(qid)
            wikidata_classes: Dict[str, WikidataClass] = {}
            cycle_detector: Set[Tuple[str, str]] = set()
            adjacency_list: Dict[str, Set[str]] = {}

            for class_qid, subclass_qid, class_label, subclass_label in results:
                wikidata_classes.setdefault(
                    class_qid, WikidataClass(class_qid, class_label)
                )
                wikidata_classes.setdefault(
                    subclass_qid, WikidataClass(subclass_qid, subclass_label)
                )
                adjacency_list.setdefault(class_qid, set()).add(subclass_qid)
        except (ValueError, KeyError, HTTPError) as e:
            logger.exception(e)
            return {qid: WikidataClass(qid, f"Class {qid}")}

        queue = deque([qid])
        visited = set()

        while queue:
            current_qid = queue.popleft()
            if current_qid in visited:
                continue
            visited.add(current_qid)

            # Ensure the starting QID is in the dictionary
            if current_qid not in wikidata_classes:
                wikidata_classes[current_qid] = WikidataClass(
                    current_qid, f"Class {current_qid}"
                )

            if current_qid in adjacency_list:
                for subclass_qid in adjacency_list[current_qid]:
                    if (current_qid, subclass_qid) not in cycle_detector:
                        wikidata_classes[current_qid].subclasses.append(
                            wikidata_classes[subclass_qid]
                        )
                        queue.append(subclass_qid)
                        cycle_detector.add((current_qid, subclass_qid))

        return wikidata_classes

    @staticmethod
    @lru_cache(maxsize=256)
    def _superclasses_cached(qid: str) -> Tuple[Tuple[str, str], ...]:
        """
        Cached helper for superclasses — returns tuple of (class_qid, superclass_qid, class_label, superclass_label).
        Returns empty tuple on error to avoid caching failures.
        """
        try:
            query = f"""
            SELECT DISTINCT ?class ?classLabel ?superclass ?superclassLabel
            WHERE
            {{
                wd:{qid} wdt:P279* ?class.
                ?class wdt:P279 ?superclass.
                SERVICE wikibase:label {{bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
            }}
            """
            reply: Dict[str, Any] = WikiDataAPIClient.sparql_query(query)
            results: List[Tuple[str, str]] = []
            if "results" in reply:
                for b in reply["results"]["bindings"]:
                    superclass_qid = b["superclass"]["value"].rsplit("/", 1)[-1]
                    class_qid = b["class"]["value"].rsplit("/", 1)[-1]
                    superclass_label = b["superclassLabel"]["value"]
                    class_label = b["classLabel"]["value"]
                    results.append(
                        (class_qid, superclass_qid, class_label, superclass_label)
                    )
            return tuple(results)
        except Exception as e:
            logger.warning(f"Failed to fetch superclasses for {qid}: {e}")
            return ()

    @staticmethod
    @lru_cache(maxsize=256)
    def _subclasses_cached(qid: str) -> Tuple[Tuple[str, str], ...]:
        """
        Cached helper for subclasses — returns tuple of (class_qid, subclass_qid, class_label, subclass_label).
        Returns empty tuple on error to avoid caching failures.
        """
        try:
            query: str = f"""
                SELECT DISTINCT ?class ?classLabel ?subclass ?subclassLabel
                WHERE
                {{
                    ?subclass wdt:P279 wd:{qid}.
                    ?subclass wdt:P279 ?class.
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
                }}
                LIMIT 1000
                """
            reply: Dict[str, Any] = WikiDataAPIClient.sparql_query(query)
            results: List[Tuple[str, str]] = []
            if "results" in reply:
                for b in reply["results"]["bindings"]:
                    subclass_qid = b["subclass"]["value"].rsplit("/", 1)[-1]
                    class_qid = b["class"]["value"].rsplit("/", 1)[-1]
                    subclass_label = b["subclassLabel"]["value"]
                    class_label = b["classLabel"]["value"]
                    results.append(
                        (class_qid, subclass_qid, class_label, subclass_label)
                    )
            return tuple(results)
        except Exception as e:
            logger.warning(f"Failed to fetch subclasses for {qid}: {e}")
            return ()

    @staticmethod
    def superclasses(qid: str) -> Dict[str, WikidataClass]:
        """
        Returns the Wikidata class with all its superclasses for the given QID.

        Parameters
        ----------
        qid: str
            Wikidata QID (e.g., 'Q146' for house cat).

        Returns
        -------
        classes: Dict[str, WikidataClass]
            A dictionary of WikidataClass objects, where the keys are QIDs and the values are the corresponding
        """
        try:
            results = WikiDataAPIClient._superclasses_cached(qid)
            wikidata_classes: Dict[str, WikidataClass] = {}
            cycle_detector: Set[Tuple[str, str]] = set()
            adjacency_list: Dict[str, Set[str]] = {}

            for class_qid, superclass_qid, class_label, superclass_label in results:
                wikidata_classes.setdefault(
                    class_qid, WikidataClass(class_qid, class_label)
                )
                wikidata_classes.setdefault(
                    superclass_qid, WikidataClass(superclass_qid, superclass_label)
                )
                adjacency_list.setdefault(class_qid, set()).add(superclass_qid)
        except (ValueError, KeyError, HTTPError) as e:
            logger.exception(e)
            return {qid: WikidataClass(qid, f"Class {qid}")}
        queue = deque([qid])
        visited = set()

        while queue:
            current_qid = queue.popleft()
            if current_qid in visited:
                continue
            visited.add(current_qid)

            if current_qid in adjacency_list:
                for superclass_qid in adjacency_list[current_qid]:
                    if (current_qid, superclass_qid) not in cycle_detector:
                        wikidata_classes[current_qid].superclasses.append(
                            wikidata_classes[superclass_qid]
                        )
                        queue.append(superclass_qid)
                        cycle_detector.add((current_qid, superclass_qid))

        return wikidata_classes

    @staticmethod
    def search_term(
        search_term: str,
        language: LanguageCode,
        url: str = WIKIDATA_SEARCH_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[WikidataSearchResult]:
        """
        Search for a term in the WikiData.
        Parameters
        ----------
        search_term: str
            The term to search for.
        language: str
            The language to search in.
        url: str
            The URL of the WikiData search API.
        timeout: int (Default: DEFAULT_TIMEOUT)
            The timeout for the request.

        Returns
        -------
        search_results_dict: List[WikidataSearchResult]
            The search results.
        """
        search_results_dict: List[WikidataSearchResult] = []
        headers: Dict[str, str] = WikiDataAPIClient.headers()
        # Use persistent session for connection reuse
        params: Dict[str, str] = {
            "action": "wbsearchentities",
            "format": "json",
            "language": language,
            "search": search_term,
        }
        response: Response = _wikidata_session.get(
            url, params=params, timeout=timeout, headers=headers
        )

        # Check the response status code
        if not response.ok:
            raise WikiDataAPIException(
                f"Search request failed with status code : {response.status_code}. "
                f"URL:= {url}"
            )
        search_result_dict_full: Dict[str, Any] = response.json()
        for search_result_dict in search_result_dict_full["search"]:
            search_results_dict.append(
                WikidataSearchResult.from_dict(search_result_dict)
            )
            return search_results_dict

    @staticmethod
    def __wikidata_task__(qid: str) -> WikidataThing:
        """Retrieve a single Wikidata thing.

        Parameters
        ----------
        qid: str
            QID of the entity.

        Returns
        -------
        instance: WikidataThing
            Single wikidata thing
        """
        try:
            if wikidata_cache.qid_in_cache(qid):
                return wikidata_cache.get_wikidata_object(qid)
            w_thing = WikidataThing.from_wikidata(__waiting_request__(qid))
            # Add the thing to the cache
            wikidata_cache.cache_wikidata_object(w_thing)
            return w_thing
        except (ValueError, KeyError, HTTPError) as e:
            logger.exception(e)
            raise WikiDataAPIException(e) from e

    @staticmethod
    def __wikidata_multiple_task__(qids: List[str]) -> List[WikidataThing]:
        """Retrieve multiple Wikidata things.

        Parameters
        ----------
        qids: List[str]
            QIDs of the entities.

        Returns
        -------
        instances: List[WikidataThing]
            List of wikidata things
        """
        try:
            results: List[WikidataThing] = []
            if len(qids) > 0:
                for e in __waiting_multi_request__(qids):
                    w_thing = WikidataThing.from_wikidata(e)
                    results.append(w_thing)
            return results
        except (ValueError, KeyError, HTTPError) as e:
            logger.exception(e)
            raise WikiDataAPIException(e) from e

    @staticmethod
    def retrieve_entity(qid: str) -> WikidataThing:
        """
        Retrieve a single Wikidata thing.

        Parameters
        ----------
        qid: str
            QID of the entity.

        Returns
        -------
        instance: WikidataThing
            Single wikidata thing
        """
        return WikiDataAPIClient.__wikidata_task__(qid)

    @staticmethod
    def retrieve_entities(
        qids: Union[List[str], Set[str]],
        progress: Optional[Callable[[int, int], None]] = None,
    ) -> List[WikidataThing]:
        """
        Retrieve multiple Wikidata things.
        Parameters
        ----------
        qids: List[str]
            QIDs of the entities.
        progress: Optional[Callable[[int, int], None]]
            Optional callback function to report progress.

        Returns
        -------
        instances: List[WikidataThing]
            List of wikidata things.
        """
        pulled: List[WikidataThing] = []
        task_size: int = len(qids)
        if len(qids) == 0:
            return []
        missing_qids: List[str] = []
        for qid in qids:
            if not wikidata_cache.qid_in_cache(qid):
                if qid and qid.startswith("Q") and len(qid) > 1:
                    missing_qids.append(qid)
            else:
                pulled.append(wikidata_cache.get_wikidata_object(qid))
        ctr: int = len(pulled)
        if progress:
            progress(len(pulled), task_size)
        jobs: List[List[str]] = list(chunks(list(missing_qids), API_LIMIT))
        num_processes: int = min(len(jobs), multiprocessing.cpu_count())
        if num_processes > 1:
            with Pool(processes=num_processes) as pool:
                # Wikidata thing is not support in multiprocessing
                for lst in pool.imap_unordered(__waiting_multi_request__, jobs):
                    for w_dict in lst:
                        w_thing = WikidataThing.from_wikidata(w_dict)
                        wikidata_cache.cache_wikidata_object(w_thing)
                        pulled.append(w_thing)
                        ctr += 1
                        if progress:
                            progress(ctr, task_size)
        else:
            results = WikiDataAPIClient.__wikidata_multiple_task__(jobs[0])
            for w_thing in results:
                wikidata_cache.cache_wikidata_object(w_thing)
                ctr += 1
                if progress:
                    progress(ctr, task_size)
            pulled.extend(results)
        return pulled

    @staticmethod
    def wikiproperty(pid: str) -> WikidataProperty:
        """
        Retrieve a single Wikidata property.

        Parameters
        ----------
        pid: str
            PID of the property.

        Returns
        -------
        instance: WikidataProperty
            Single wikidata property
        """
        try:
            # if wikidata_cache.get_property(pid):
            #    return wikidata_cache.get_property(pid)
            w_property = WikidataProperty.from_wikidata(__waiting_request__(pid))
            # Add the property to the cache
            wikidata_cache.cache_property(w_property)
            return w_property
        except (ValueError, KeyError, HTTPError) as e:
            logger.exception(e)
            raise WikiDataAPIException(e) from e
