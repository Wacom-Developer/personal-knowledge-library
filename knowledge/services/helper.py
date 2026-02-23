# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
from typing import Any, Union
from typing import Dict, List, Iterator

import loguru

from knowledge.base.entity import (
    DATA_PROPERTIES_TAG,
    DATA_PROPERTY_TAG,
    VALUE_TAG,
    DESCRIPTION_TAG,
    TYPE_TAG,
    LABELS_TAG,
    IS_MAIN_TAG,
    DESCRIPTIONS_TAG,
    LOCALE_TAG,
    INDEXING_NEL_TARGET,
    INDEXING_VECTOR_SEARCH_TARGET,
    INDEXING_FULLTEXT_TARGET,
    TARGETS_TAG,
    INDEXING_VECTOR_SEARCH_DOCUMENT_TARGET,
)
from knowledge.base.language import SUPPORTED_LOCALES
from knowledge.base.ontology import OntologyPropertyReference
from knowledge.base.ontology import ThingObject, EN_US
from knowledge.services import TENANT_RIGHTS_TAG

__all__ = [
    "split_updates",
    "entity_payload",
    "RELATIONS_BULK_LIMIT",
]

RELATIONS_BULK_LIMIT: int = 30
"""
In one request only 30 relations can be created, otherwise the database operations are too many.
"""
logger = loguru.logger


def split_updates(
    updates: Dict[OntologyPropertyReference, List[str]],
    max_operations: int = RELATIONS_BULK_LIMIT,
) -> Iterator[List[Dict[str, Union[str, List[str]]]]]:
    """

    Parameters
    ----------
    updates: Dict[OntologyPropertyReference, List[str]]
        The updates to split into batches.
    max_operations: int (default: RELATIONS_BULK_LIMIT)
        The maximum number of operations

    Yields
    -------
    batch: List[Dict[str, Union[str, List[str]]]]
        The batch of updates to process.
    """
    batch: List[Dict[str, Union[str, List[str]]]] = []
    current_batch_size: int = 0
    for predicate, targets in updates.items():
        target_entry: Dict[str, Union[str, List[str]]] = {
            "relation": predicate.iri,
            "targets": [],
        }
        batch.append(target_entry)
        for target in targets:
            if current_batch_size >= max_operations:
                yield batch
                target_entry = {"relation": predicate.iri, "targets": []}
                batch = [target_entry]
                current_batch_size = 0
            targets_list = target_entry["targets"]
            if isinstance(targets_list, list):
                targets_list.append(target)
            current_batch_size += 1
    if current_batch_size > 0:
        yield batch


def entity_payload(entity: ThingObject) -> Dict[str, Any]:
    """
    Create the payload for the entity.
    Parameters
    ----------
    entity: ThingObject
        The entity to create the payload for.

    Returns
    -------
    Dict[str, Any]
        The payload for the entity.
    """
    # Different localized content
    labels: List[Dict[str, Any]] = []
    descriptions: List[Dict[str, Any]] = []
    literals: List[Dict[str, Any]] = []
    # Add description in different languages
    for desc in entity.description:
        if desc is None or desc.content is None:
            logger.warning("Description is None")
            continue

        if len(desc.content) > 0 and not desc.content == " ":
            descriptions.append({DESCRIPTION_TAG: desc.content, LOCALE_TAG: desc.language_code})

    # Labels are tagged as the main label
    for label in entity.label:
        if label is not None and label.content is not None and len(label.content) > 0 and label.content != " ":
            labels.append(
                {
                    VALUE_TAG: label.content,
                    LOCALE_TAG: label.language_code,
                    IS_MAIN_TAG: True,
                }
            )
    # Aliases are no main labels
    for label in entity.alias:
        if label is not None and len(label.content) > 0 and label.content != " ":
            labels.append(
                {
                    VALUE_TAG: label.content,
                    LOCALE_TAG: label.language_code,
                    IS_MAIN_TAG: False,
                }
            )
    # Labels are tagged as the main label
    for _, list_literals in entity.data_properties.items():
        for li in list_literals:
            if li.data_property_type:
                literals.append(
                    {
                        VALUE_TAG: li.value,
                        LOCALE_TAG: (
                            li.language_code if li.language_code and li.language_code in SUPPORTED_LOCALES else EN_US
                        ),
                        DATA_PROPERTY_TAG: li.data_property_type.iri,
                    }
                )
    payload: Dict[str, Any] = {
        TYPE_TAG: entity.concept_type.iri,
        DESCRIPTIONS_TAG: descriptions,
        LABELS_TAG: labels,
        DATA_PROPERTIES_TAG: literals,
    }
    targets: List[str] = []
    if entity.use_vector_index:
        targets.append(INDEXING_VECTOR_SEARCH_TARGET)
    if entity.use_vector_index_document:
        targets.append(INDEXING_VECTOR_SEARCH_DOCUMENT_TARGET)
    if entity.use_full_text_index:
        targets.append(INDEXING_FULLTEXT_TARGET)
    if entity.use_for_nel:
        targets.append(INDEXING_NEL_TARGET)
    payload[TARGETS_TAG] = targets
    if entity.tenant_access_right:
        payload[TENANT_RIGHTS_TAG] = entity.tenant_access_right.to_list()
    return payload
