# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import functools
import multiprocessing
from typing import Any

from tqdm import tqdm

from knowledge.public.helper import CLAIMS_TAG, PID_TAG, LABEL_TAG, QID_TAG
from knowledge.public.wikidata import LITERALS_TAG, WikidataThing, WikiDataAPIClient


def __relations__(thing: dict[str, Any], wikidata: set[str]) -> tuple[str, list[dict[str, Any]]]:
    relations: list[dict[str, Any]] = []
    for _, p_value in thing[CLAIMS_TAG].items():
        for v in p_value[LITERALS_TAG]:
            if isinstance(v, dict) and v.get('type') in ['wikibase-entityid', 'wikibase-item']:
                ref_qid = v['value']['id']
                prop = p_value[PID_TAG][LABEL_TAG]
                if ref_qid in wikidata:
                    relations.append({
                        'subject': {
                            'qid': thing[QID_TAG],
                        },
                        'predicate': {
                            'pid': p_value[PID_TAG][PID_TAG],
                            'label': prop
                        },
                        'target': {
                            'qid': ref_qid
                        }
                    })
    return thing[QID_TAG], relations


def wikidata_extractor_entities(qids: set[str]) -> dict[str, WikidataThing]:
    """
    Extracts an entity from Wikidata.

    Parameters
    ----------
    qids: set[str]
        Set of unique QIDs

    Returns
    -------
    wikidata_extractor: dict[str, WikidataThing]
        Wikidata map
    """
    return dict([(e.qid, e) for e in WikiDataAPIClient.retrieve_entities(qids)])


def wikidata_relations_extractor(wikidata: dict[str, WikidataThing]) \
        -> dict[str, list[dict[str, Any]]]:
    relations: dict[str, list[dict[str, Any]]] = {}
    quis: set[str] = set(wikidata.keys())
    num_processes: int = min(len(wikidata), multiprocessing.cpu_count())
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Wikidata thing is not support in multiprocessing
        with tqdm(total=round(len(wikidata) / num_processes), desc='Check Wikidata relations.') as pbar:
            for qid, rels in pool.map(functools.partial(__relations__, wikidata=quis),
                                      [e.__dict__() for e in wikidata.values()]):
                relations[qid] = rels
                pbar.update(1)
    return relations
