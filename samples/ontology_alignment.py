# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom Authors. All Rights Reserved.
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
Aligning a tenant ontology with an ontology defined in an RDF file
==================================================================

Reads the ontology a tenant currently has, compares it with a target ontology held in an
RDF file, and brings the tenant up to the target:

1. Extract the live state: the context, its concept classes and its properties. With
   ``--export`` the ontology is also written to disk as RDF, which is the artifact to keep
   before changing anything.
2. Parse the target ontology from the RDF file.
3. Compute an alignment plan: what has to be created, what has drifted and needs updating,
   and what exists in the tenant but not in the file.
4. Print the plan. Without ``--apply`` the script stops here and changes nothing.
5. Apply the plan, commit the ontology, and let the graph service pick up the new version.

The alignment is deliberately **not** destructive. Concepts and properties that live in the
tenant but not in the RDF file are reported and left alone, because entities in the graph
may still be using them. Labels and comments, on the other hand, are replaced by what the
RDF file declares -- the file is the source of truth for them -- so the plan spells out
which values a run would remove.

Requires a shadow user with the **TenantAdmin** role; ordinary users may read the ontology
but not change it.

Usage
-----
>>> python ontology_alignment.py -t <tenant-api-key> -u <external-user-id> -r <target.rdf>
>>> python ontology_alignment.py -t <key> -u <user> -r target.rdf --export live.rdf --apply
"""

import argparse
import enum
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

import loguru
from rdflib import Graph

from knowledge.base.language import EN
from knowledge.base.ontology import (
    Comment,
    DataPropertyType,
    Ontology,
    OntologyClass,
    OntologyClassReference,
    OntologyContext,
    OntologyLabel,
    OntologyProperty,
    OntologyPropertyReference,
    OntologyUpdateStatus,
    PREFERRED_LABEL,
    PendingOntologyVersion,
    RESOURCE,
    THING_CLASS,
    ontology_import,
)
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.session import PermanentSession

logger = loguru.logger

# ------------------------------- Constants ----------------------------------------------------------------------------
ADMIN_ROLE: str = "TenantAdmin"
CONTEXT_NAME: str = "core"

OWL_THING: str = "http://www.w3.org/2002/07/owl#Thing"
TOP_DATA_PROPERTY: str = "http://www.w3.org/2002/07/owl#topDataProperty"
TOP_OBJECT_PROPERTY: str = "http://www.w3.org/2002/07/owl#topObjectProperty"

ROOT_CLASS_IRIS: Set[str] = {THING_CLASS.iri, RESOURCE, OWL_THING}
"""Superclasses that need no counterpart in the tenant: every concept ends up below them."""

TOP_PROPERTY_IRIS: Set[str] = {TOP_DATA_PROPERTY, TOP_OBJECT_PROPERTY}
"""OWL roots of the property hierarchy. The service rejects them as an explicit super property."""

LABEL_PREDICATE_IRI: str = str(PREFERRED_LABEL)
"""The predicate carrying ontology labels. The service lists it as a property but never
declares it in an RDF export, so it would otherwise be reported as missing on every run."""

REQUIRED_IDLE_POLLS: int = 2
"""Consecutive idle readings needed before an apply counts as finished."""


class Outcome(str, enum.Enum):
    """Result of a single planned change."""

    APPLIED = "applied"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class AlignmentPlan:
    """Everything a run would change, grouped by the call that would change it.

    Parameters
    ----------
    new_concepts: List[OntologyClass]
        Concept classes the RDF file declares and the tenant lacks.
    new_data_properties: List[OntologyProperty]
        Data properties the RDF file declares and the tenant lacks.
    new_object_properties: List[OntologyProperty]
        Object properties the RDF file declares and the tenant lacks.
    updated_concepts: List[Tuple[OntologyClass, OntologyClass]]
        Concepts whose labels or comments drifted, as (target, live) pairs.
    updated_properties: List[Tuple[OntologyProperty, OntologyProperty]]
        Properties whose labels or comments drifted, as (target, live) pairs.
    added_domains: List[Tuple[OntologyProperty, List[OntologyClassReference]]]
        Domains the RDF file declares for an existing property and the tenant lacks.
    added_ranges: List[Tuple[OntologyProperty, List[Union[OntologyClassReference, DataPropertyType]]]]
        Ranges the RDF file declares for an existing property and the tenant lacks.
    extra_concepts: List[OntologyClassReference]
        Concepts the tenant has and the RDF file does not. Reported only.
    extra_properties: List[OntologyPropertyReference]
        Properties the tenant has and the RDF file does not. Reported only.
    """

    new_concepts: List[OntologyClass] = field(default_factory=list)
    new_data_properties: List[OntologyProperty] = field(default_factory=list)
    new_object_properties: List[OntologyProperty] = field(default_factory=list)
    updated_concepts: List[Tuple[OntologyClass, OntologyClass]] = field(default_factory=list)
    updated_properties: List[Tuple[OntologyProperty, OntologyProperty]] = field(default_factory=list)
    added_domains: List[Tuple[OntologyProperty, List[OntologyClassReference]]] = field(default_factory=list)
    added_ranges: List[Tuple[OntologyProperty, List[Union[OntologyClassReference, DataPropertyType]]]] = field(
        default_factory=list
    )
    extra_concepts: List[OntologyClassReference] = field(default_factory=list)
    extra_properties: List[OntologyPropertyReference] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Is the tenant already aligned with the RDF file?"""
        return not (
            self.new_concepts
            or self.new_data_properties
            or self.new_object_properties
            or self.updated_concepts
            or self.updated_properties
            or self.added_domains
            or self.added_ranges
        )


# ------------------------------- Helpers ------------------------------------------------------------------------------
def range_iri(value: Union[OntologyClassReference, DataPropertyType]) -> str:
    """Resolve a property range entry to its IRI.

    Object-property ranges are concept classes, data-property ranges are XSD data types, and
    the service reports both as plain IRIs. Comparing IRIs is therefore the only way to line
    up a parsed range against a live one.

    Parameters
    ----------
    value: Union[OntologyClassReference, DataPropertyType]
        Range entry to resolve.

    Returns
    -------
    iri: str
        IRI of the range entry.
    """
    return str(value.value) if isinstance(value, DataPropertyType) else value.iri


def localized(entries: Sequence[Union[OntologyLabel, Comment]]) -> Set[Tuple[str, str]]:
    """Reduce labels or comments to a comparable set of (text, language) pairs.

    Parameters
    ----------
    entries: Sequence[Union[OntologyLabel, Comment]]
        Labels or comments of a concept or property.

    Returns
    -------
    values: Set[Tuple[str, str]]
        Set of (content, language code) pairs.
    """
    # A literal without xml:lang is imported as the default language, while the service
    # reports the same value with an empty language code. Normalizing keeps that from
    # reading as drift.
    return {(entry.content, str(entry.language_code) or EN) for entry in entries}


def load_target_ontology(path: Path) -> Ontology:
    """Read the target ontology from an RDF file.

    `ontology_import` parses RDF/XML only, so any other syntax rdflib understands -- Turtle,
    N-Triples, JSON-LD -- is re-serialized to RDF/XML first.

    Parameters
    ----------
    path: Path
        RDF file holding the target ontology.

    Returns
    -------
    ontology: Ontology
        Parsed target ontology.

    Raises
    ------
    SystemExit
        If the file cannot be parsed, or declares a data type the service does not support.
    """
    content: str = path.read_text(encoding="utf-8")
    if path.suffix.lower() not in (".rdf", ".owl", ".xml"):
        try:
            content = Graph().parse(data=content, format=None, publicID=path.as_uri()).serialize(format="xml")
        except Exception as exception:  # pylint: disable=broad-except
            print(f"'{path}' could not be parsed as RDF: {exception}")
            sys.exit(1)
    try:
        return ontology_import(content)
    except KeyError as key_error:
        print(f"'{path}' uses a data type the ontology service does not support: {key_error}")
        sys.exit(1)


def fetch_live_state(
    client: OntologyService, context: str
) -> Tuple[Dict[str, OntologyClass], Dict[str, OntologyProperty]]:
    """Extract the ontology the tenant currently has.

    Parameters
    ----------
    client: OntologyService
        Ontology client bound to the tenant admin.
    context: str
        Name of the context.

    Returns
    -------
    state: Tuple[Dict[str, OntologyClass], Dict[str, OntologyProperty]]
        Concepts and properties of the context, both keyed by IRI.
    """
    concepts: Dict[str, OntologyClass] = {c.reference.iri: c for c in client.concepts_types(context)}
    properties: Dict[str, OntologyProperty] = {p.reference.iri: p for p in client.properties_types(context)}
    return concepts, properties


def build_plan(
    target: Ontology,
    live_concepts: Dict[str, OntologyClass],
    live_properties: Dict[str, OntologyProperty],
) -> AlignmentPlan:
    """Compare the target ontology with the live one.

    Parameters
    ----------
    target: Ontology
        Ontology parsed from the RDF file.
    live_concepts: Dict[str, OntologyClass]
        Concepts of the tenant, keyed by IRI.
    live_properties: Dict[str, OntologyProperty]
        Properties of the tenant, keyed by IRI.

    Returns
    -------
    plan: AlignmentPlan
        Changes that would align the tenant with the RDF file.
    """
    plan: AlignmentPlan = AlignmentPlan()
    for concept in target.classes:
        # An RDF export declares the roots of the hierarchy, but the service does not list
        # them as concepts of the context and refuses to create them.
        if concept.reference.iri in ROOT_CLASS_IRIS:
            continue
        live_concept: Optional[OntologyClass] = live_concepts.get(concept.reference.iri)
        if live_concept is None:
            plan.new_concepts.append(concept)
        elif localized(concept.labels) != localized(live_concept.labels) or localized(concept.comments) != localized(
            live_concept.comments
        ):
            plan.updated_concepts.append((concept, live_concept))

    for prop in target.data_properties + target.object_properties:
        live_property: Optional[OntologyProperty] = live_properties.get(prop.reference.iri)
        if live_property is None:
            if prop.is_data_property:
                plan.new_data_properties.append(prop)
            else:
                plan.new_object_properties.append(prop)
            continue
        if localized(prop.labels) != localized(live_property.labels) or localized(prop.comments) != localized(
            live_property.comments
        ):
            plan.updated_properties.append((prop, live_property))
        live_domains: Set[str] = {d.iri for d in live_property.domains}
        missing_domains: List[OntologyClassReference] = [d for d in prop.domains if d.iri not in live_domains]
        if missing_domains:
            plan.added_domains.append((prop, missing_domains))
        live_ranges: Set[str] = {range_iri(r) for r in live_property.ranges}
        missing_ranges: List[Union[OntologyClassReference, DataPropertyType]] = [
            r for r in prop.ranges if range_iri(r) not in live_ranges
        ]
        if missing_ranges:
            plan.added_ranges.append((prop, missing_ranges))

    target_concept_iris: Set[str] = {c.reference.iri for c in target.classes}
    target_property_iris: Set[str] = {p.reference.iri for p in target.data_properties + target.object_properties}
    plan.extra_concepts = [
        c.reference for iri, c in live_concepts.items() if iri not in target_concept_iris and iri not in ROOT_CLASS_IRIS
    ]
    plan.extra_properties = [
        p.reference
        for iri, p in live_properties.items()
        if iri not in target_property_iris and iri != LABEL_PREDICATE_IRI
    ]
    return plan


def print_drift(
    target: Sequence[Union[OntologyLabel, Comment]],
    live: Sequence[Union[OntologyLabel, Comment]],
    kind: str,
) -> bool:
    """Print what an update would add and remove for one set of localized values.

    Parameters
    ----------
    target: Sequence[Union[OntologyLabel, Comment]]
        Values the RDF file declares.
    live: Sequence[Union[OntologyLabel, Comment]]
        Values the tenant currently has.
    kind: str
        Name of the value set, used as the line label.

    Returns
    -------
    removes: bool
        True if applying the update would drop a value the tenant currently has.
    """
    added: Set[Tuple[str, str]] = localized(target) - localized(live)
    removed: Set[Tuple[str, str]] = localized(live) - localized(target)
    if added:
        print(f"      {kind:<9} + " + ", ".join(f"'{text}'@{lang}" for text, lang in sorted(added)))
    if removed:
        print(f"      {kind:<9} - " + ", ".join(f"'{text}'@{lang}" for text, lang in sorted(removed)))
    return bool(removed)


def print_plan(plan: AlignmentPlan) -> None:
    """Print the alignment plan.

    Parameters
    ----------
    plan: AlignmentPlan
        Plan to print.
    """
    print("-" * 120)
    print(" Alignment plan")
    print("-" * 120)
    for concept in plan.new_concepts:
        parent: str = concept.subclass_of.iri if concept.subclass_of else THING_CLASS.iri
        print(f"  create concept          {concept.reference.iri} (subclass of {parent})")
    for prop in plan.new_data_properties:
        print(f"  create data property    {prop.reference.iri}")
    for prop in plan.new_object_properties:
        print(f"  create object property  {prop.reference.iri}")
    removes: bool = False
    for concept, live_concept in plan.updated_concepts:
        print(f"  update concept          {concept.reference.iri}")
        removes = print_drift(concept.labels, live_concept.labels, "labels") or removes
        removes = print_drift(concept.comments, live_concept.comments, "comments") or removes
    for prop, live_property in plan.updated_properties:
        print(f"  update property         {prop.reference.iri}")
        removes = print_drift(prop.labels, live_property.labels, "labels") or removes
        removes = print_drift(prop.comments, live_property.comments, "comments") or removes
    for prop, domains in plan.added_domains:
        print(f"  add domains             {prop.reference.iri}: {', '.join(d.iri for d in domains)}")
    for prop, ranges in plan.added_ranges:
        print(f"  add ranges              {prop.reference.iri}: {', '.join(range_iri(r) for r in ranges)}")
    if removes:
        print("\n  Note: the lines marked '-' would be removed, because the RDF file does not declare them.")
        print("        Add them to the file if the tenant should keep them.")
    if plan.is_empty:
        print("  nothing to do, the tenant already matches the RDF file")
    if plan.extra_concepts or plan.extra_properties:
        print("-" * 120)
        print(" Only in the tenant, left untouched")
        print("-" * 120)
        for concept_ref in sorted(plan.extra_concepts, key=lambda r: r.iri):
            print(f"  concept                 {concept_ref.iri}")
        for property_ref in sorted(plan.extra_properties, key=lambda r: r.iri):
            print(f"  property                {property_ref.iri}")


# ------------------------------- Ordering -----------------------------------------------------------------------------
def order_concepts(
    concepts: List[OntologyClass], known_iris: Set[str]
) -> Tuple[List[OntologyClass], List[OntologyClass]]:
    """Order new concepts so that every superclass is created before its subclasses.

    Parameters
    ----------
    concepts: List[OntologyClass]
        Concepts to create.
    known_iris: Set[str]
        IRIs of the concepts the tenant already has.

    Returns
    -------
    ordered: Tuple[List[OntologyClass], List[OntologyClass]]
        Concepts in a creatable order, and the ones whose superclass is nowhere to be found.
    """
    pending: Dict[str, OntologyClass] = {c.reference.iri: c for c in concepts}
    resolved: Set[str] = set(known_iris) | ROOT_CLASS_IRIS
    ordered: List[OntologyClass] = []
    progress: bool = True
    while pending and progress:
        progress = False
        for iri in list(pending):
            concept: OntologyClass = pending[iri]
            parent: str = concept.subclass_of.iri if concept.subclass_of else THING_CLASS.iri
            if parent in resolved:
                ordered.append(concept)
                resolved.add(iri)
                del pending[iri]
                progress = True
    return ordered, list(pending.values())


def order_properties(
    properties: List[OntologyProperty], known_iris: Set[str]
) -> Tuple[List[OntologyProperty], List[OntologyProperty]]:
    """Order new properties so that every super property is created before its sub properties.

    Parameters
    ----------
    properties: List[OntologyProperty]
        Properties to create.
    known_iris: Set[str]
        IRIs of the properties the tenant already has.

    Returns
    -------
    ordered: Tuple[List[OntologyProperty], List[OntologyProperty]]
        Properties in a creatable order, and the ones whose super property is missing.
    """
    pending: Dict[str, OntologyProperty] = {p.reference.iri: p for p in properties}
    resolved: Set[str] = set(known_iris) | TOP_PROPERTY_IRIS
    ordered: List[OntologyProperty] = []
    progress: bool = True
    while pending and progress:
        progress = False
        for iri in list(pending):
            prop: OntologyProperty = pending[iri]
            if prop.subproperty_of is None or prop.subproperty_of.iri in resolved:
                ordered.append(prop)
                resolved.add(iri)
                del pending[iri]
                progress = True
    return ordered, list(pending.values())


def super_property(prop: OntologyProperty) -> Optional[OntologyPropertyReference]:
    """Resolve the super property to pass to the service.

    The OWL roots of the property hierarchy are implicit: the service rejects them as an
    explicit ``subPropertyOf``.

    Parameters
    ----------
    prop: OntologyProperty
        Property to inspect.

    Returns
    -------
    reference: Optional[OntologyPropertyReference]
        Super property, or None if the property sits directly below an OWL root.
    """
    if prop.subproperty_of is None or prop.subproperty_of.iri in TOP_PROPERTY_IRIS:
        return None
    return prop.subproperty_of


# ------------------------------- Applying -----------------------------------------------------------------------------
@dataclass
class Summary:
    """Counts of what a run actually did.

    Parameters
    ----------
    created: int
        Concepts and properties created.
    updated: int
        Concepts and properties whose labels, comments, domains or ranges were changed.
    skipped: int
        Changes left out because a type they depend on is missing.
    failed: int
        Changes the service rejected.
    """

    created: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0

    def record(self, outcome: Outcome, created: bool = False) -> None:
        """Count one planned change.

        Parameters
        ----------
        outcome: Outcome
            How the change ended.
        created: bool (default:= False)
            True if an applied change created a new type rather than modifying one.
        """
        if outcome is Outcome.APPLIED:
            if created:
                self.created += 1
            else:
                self.updated += 1
        elif outcome is Outcome.SKIPPED:
            self.skipped += 1
        else:
            self.failed += 1

    @property
    def has_changes(self) -> bool:
        """Did anything reach the ontology?"""
        return self.created > 0 or self.updated > 0


def superclass_of(concept: OntologyClass) -> OntologyClassReference:
    """Resolve the superclass to pass to the service.

    A concept without a superclass, or one rooted in ``rdfs:Resource`` or ``owl:Thing``,
    hangs below the Wacom root class instead.

    Parameters
    ----------
    concept: OntologyClass
        Concept to inspect.

    Returns
    -------
    reference: OntologyClassReference
        Superclass to create the concept under.
    """
    if concept.subclass_of is None or concept.subclass_of.iri in ROOT_CLASS_IRIS:
        return THING_CLASS
    return concept.subclass_of


def apply_plan(
    client: OntologyService,
    context: str,
    plan: AlignmentPlan,
    known_concepts: Set[str],
    known_properties: Set[str],
) -> Summary:
    """Apply the alignment plan to the tenant ontology.

    Dependencies decide the order: a concept cannot be created before its superclass, and a
    property cannot be created before the concepts of its domain and range. Anything the
    service rejects is logged and counted, and the run carries on with the next change.

    Parameters
    ----------
    client: OntologyService
        Ontology client bound to the tenant admin.
    context: str
        Name of the context.
    plan: AlignmentPlan
        Changes to apply.
    known_concepts: Set[str]
        IRIs of the concepts the tenant already has.
    known_properties: Set[str]
        IRIs of the properties the tenant already has.

    Returns
    -------
    summary: Summary
        Counts of what was created, updated, skipped and rejected.
    """
    summary: Summary = Summary()
    available_concepts: Set[str] = set(known_concepts)
    available_properties: Set[str] = set(known_properties)

    # Concepts first: a subclass is only creatable once its superclass exists.
    ordered_concepts, unresolved_concepts = order_concepts(plan.new_concepts, available_concepts)
    for concept in unresolved_concepts:
        logger.warning(
            f"Skipping concept {concept.reference.iri}: its superclass "
            f"{concept.subclass_of.iri if concept.subclass_of else '?'} is neither in the tenant nor in the RDF file."
        )
        summary.record(Outcome.SKIPPED)
    for concept in ordered_concepts:
        try:
            client.create_concept(
                context=context,
                reference=concept.reference,
                subclass_of=superclass_of(concept),
                labels=concept.labels,
                comments=concept.comments,
            )
            available_concepts.add(concept.reference.iri)
            summary.record(Outcome.APPLIED, created=True)
            print(f"  created concept          {concept.reference.iri}")
        except WacomServiceException as exception:
            logger.error(
                f"Creating concept {concept.reference.iri} failed "
                f"[status:={exception.status_code}]: {exception.service_response}"
            )
            summary.record(Outcome.FAILED)

    # Data properties, ordered so that a super property is always created first.
    ordered_data, unresolved_data = order_properties(plan.new_data_properties, available_properties)
    for prop in unresolved_data:
        logger.warning(f"Skipping data property {prop.reference.iri}: its super property is missing.")
        summary.record(Outcome.SKIPPED)
    for prop in ordered_data:
        missing: List[str] = [d.iri for d in prop.domains if d.iri not in available_concepts]
        if missing:
            logger.warning(f"Skipping data property {prop.reference.iri}: domain {', '.join(missing)} is missing.")
            summary.record(Outcome.SKIPPED)
            continue
        try:
            client.create_data_property(
                context=context,
                reference=prop.reference,
                domains_cls=prop.domains,
                ranges_cls=[r for r in prop.ranges if isinstance(r, DataPropertyType)],
                subproperty_of=super_property(prop),
                labels=prop.labels,
                comments=prop.comments,
            )
            available_properties.add(prop.reference.iri)
            summary.record(Outcome.APPLIED, created=True)
            print(f"  created data property    {prop.reference.iri}")
        except WacomServiceException as exception:
            logger.error(
                f"Creating data property {prop.reference.iri} failed "
                f"[status:={exception.status_code}]: {exception.service_response}"
            )
            summary.record(Outcome.FAILED)

    # Object properties. An inverse can only be declared once its counterpart exists, so a
    # mutually inverse pair is created as one plain property plus one that points back at it.
    # The service then maintains both directions.
    ordered_object, unresolved_object = order_properties(plan.new_object_properties, available_properties)
    for prop in unresolved_object:
        logger.warning(f"Skipping object property {prop.reference.iri}: its super property is missing.")
        summary.record(Outcome.SKIPPED)
    for prop in ordered_object:
        types_used: List[str] = [d.iri for d in prop.domains] + [
            r.iri for r in prop.ranges if isinstance(r, OntologyClassReference)
        ]
        missing = [iri for iri in types_used if iri not in available_concepts]
        if missing:
            logger.warning(
                f"Skipping object property {prop.reference.iri}: domain or range {', '.join(missing)} is missing."
            )
            summary.record(Outcome.SKIPPED)
            continue
        inverse_of: Optional[OntologyPropertyReference] = prop.inverse_property_of
        if inverse_of is not None and inverse_of.iri not in available_properties:
            logger.info(
                f"Creating object property {prop.reference.iri} without its inverse {inverse_of.iri}, "
                f"which does not exist yet."
            )
            inverse_of = None
        try:
            client.create_object_property(
                context=context,
                reference=prop.reference,
                domains_cls=prop.domains,
                ranges_cls=[r for r in prop.ranges if isinstance(r, OntologyClassReference)],
                inverse_of=inverse_of,
                subproperty_of=super_property(prop),
                labels=prop.labels,
                comments=prop.comments,
            )
            available_properties.add(prop.reference.iri)
            summary.record(Outcome.APPLIED, created=True)
            print(f"  created object property  {prop.reference.iri}")
        except WacomServiceException as exception:
            logger.error(
                f"Creating object property {prop.reference.iri} failed "
                f"[status:={exception.status_code}]: {exception.service_response}"
            )
            summary.record(Outcome.FAILED)

    # Labels and comments of types that already exist. The icon is carried over, because the
    # patch replaces the whole set of attributes and the RDF file has no icon to offer.
    for concept, live_concept in plan.updated_concepts:
        try:
            client.update_concept(
                context=context,
                reference=concept.reference,
                icon=live_concept.icon,
                labels=concept.labels,
                comments=concept.comments,
            )
            summary.record(Outcome.APPLIED)
            print(f"  updated concept          {concept.reference.iri}")
        except WacomServiceException as exception:
            logger.error(
                f"Updating concept {concept.reference.iri} failed "
                f"[status:={exception.status_code}]: {exception.service_response}"
            )
            summary.record(Outcome.FAILED)
    for prop, live_property in plan.updated_properties:
        try:
            client.update_property(
                context=context,
                reference=prop.reference,
                icon=live_property.icon,
                labels=prop.labels,
                comments=prop.comments,
            )
            summary.record(Outcome.APPLIED)
            print(f"  updated property         {prop.reference.iri}")
        except WacomServiceException as exception:
            logger.error(
                f"Updating property {prop.reference.iri} failed "
                f"[status:={exception.status_code}]: {exception.service_response}"
            )
            summary.record(Outcome.FAILED)

    # Widening the domain or range of a property that already exists.
    for prop, domains in plan.added_domains:
        try:
            client.add_property_domains(context=context, reference=prop.reference, domains=domains)
            summary.record(Outcome.APPLIED)
            print(f"  added domains            {prop.reference.iri}: {', '.join(d.iri for d in domains)}")
        except WacomServiceException as exception:
            logger.error(
                f"Adding domains to {prop.reference.iri} failed "
                f"[status:={exception.status_code}]: {exception.service_response}"
            )
            summary.record(Outcome.FAILED)
    for prop, ranges in plan.added_ranges:
        try:
            client.add_property_ranges(context=context, reference=prop.reference, ranges=ranges)
            summary.record(Outcome.APPLIED)
            print(f"  added ranges             {prop.reference.iri}: {', '.join(range_iri(r) for r in ranges)}")
        except WacomServiceException as exception:
            logger.error(
                f"Adding ranges to {prop.reference.iri} failed "
                f"[status:={exception.status_code}]: {exception.service_response}"
            )
            summary.record(Outcome.FAILED)
    return summary


# ------------------------------- Commit and apply ---------------------------------------------------------------------
def wait_until_committed(client: OntologyService, context: str, attempts: int = 15, delay: float = 2.0) -> None:
    """Wait until a commit is observable, i.e. the context has no pending changes left.

    The apply refuses a version it has already applied, so triggering it before the commit
    is visible reports 'already applied' instead of doing the work.

    Parameters
    ----------
    client: OntologyService
        Ontology client bound to the tenant admin.
    context: str
        Name of the context.
    attempts: int (default:= 15)
        Number of polls before giving up.
    delay: float (default:= 2.0)
        Delay between two polls, in seconds.

    Raises
    ------
    RuntimeError
        If pending changes remain after the allotted attempts.
    """
    for _ in range(attempts):
        pending: PendingOntologyVersion = client.pending_version(context)
        if pending.is_empty:
            return
        time.sleep(delay)
    raise RuntimeError(f"Pending changes remained {attempts * delay:.0f}s after the commit.")


def wait_until_applied(client: WacomKnowledgeService, attempts: int = 30, delay: float = 2.0) -> None:
    """Wait until the tenant's ontology update has finished.

    `ontology_update` only **accepts** the apply; the work continues in the background while
    the tenant is locked, and every graph write is rejected until it completes.

    **Remark:**
    The service reports 'NoUpdateInProgress' both when an apply has completed and when none
    was ever started. A single idle reading would therefore return before a just-triggered
    apply registers, so two consecutive idle readings are required.

    Parameters
    ----------
    client: WacomKnowledgeService
        Graph client bound to the tenant admin.
    attempts: int (default:= 30)
        Number of status polls before giving up.
    delay: float (default:= 2.0)
        Delay between two polls, in seconds.

    Raises
    ------
    RuntimeError
        If the update failed, or did not finish within the allotted attempts.
    """
    idle_streak: int = 0
    for _ in range(attempts):
        status: OntologyUpdateStatus = client.ontology_update_status()
        if status.has_failed:
            raise RuntimeError("The ontology update failed. Resume it with ontology_update(fix=True).")
        idle_streak = idle_streak + 1 if status.is_idle else 0
        if idle_streak >= REQUIRED_IDLE_POLLS:
            return
        time.sleep(delay)
    raise RuntimeError(f"The ontology update did not finish within {attempts * delay:.0f}s.")


def publish(ontology_client: OntologyService, knowledge_client: WacomKnowledgeService, context: str) -> None:
    """Commit the ontology and make the new version available to the graph.

    Uncommitted changes are invisible to the graph service, and a committed version does
    nothing until it is applied, so both steps are needed before entities of the new types
    can be created.

    Parameters
    ----------
    ontology_client: OntologyService
        Ontology client bound to the tenant admin.
    knowledge_client: WacomKnowledgeService
        Graph client bound to the tenant admin.
    context: str
        Name of the context.
    """
    ontology_client.commit(context)
    wait_until_committed(ontology_client, context)
    print("Ontology committed.")
    try:
        knowledge_client.ontology_update()
        wait_until_applied(knowledge_client)
    except (WacomServiceException, RuntimeError) as exception:
        logger.warning(f"Applying the ontology failed ({exception}). Resuming it with fix=True.")
        knowledge_client.ontology_update(fix=True)
        wait_until_applied(knowledge_client)
    updated: Optional[OntologyContext] = ontology_client.context()
    print(f"Ontology applied. Context '{context}' is now at version {updated.version if updated else '?'}.")


# ------------------------------- Entry point --------------------------------------------------------------------------
def main() -> int:
    """Align the tenant ontology with the ontology declared in an RDF file.

    Returns
    -------
    exit_code: int
        0 if the run finished without a rejected change, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument(
        "-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument("-r", "--rdf", type=Path, required=True, help="RDF file holding the target ontology.")
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    parser.add_argument("-e", "--export", type=Path, help="Write the live ontology to this file before changing it.")
    parser.add_argument(
        "-a", "--apply", action="store_true", help="Apply the plan. Without it the script only reports."
    )
    args = parser.parse_args()

    if not args.rdf.is_file():
        print(f"'{args.rdf}' does not exist.")
        return 1

    ontology_client: OntologyService = OntologyService(service_url=args.instance)
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Ontology Alignment Demo", service_url=args.instance
    )
    session: PermanentSession = ontology_client.login(args.tenant, args.user)
    if ADMIN_ROLE not in session.roles:
        print(f"User {args.user} is not an admin user.")
        return 1
    # Each client keeps its own session table, so use_session cannot resolve a session id
    # minted by another client. Hand the token over instead.
    knowledge_client.register_token(auth_key=session.auth_token, refresh_token=session.refresh_token)

    # ------------------------------- Extract the live state -----------------------------------------------------------
    context: Optional[OntologyContext] = ontology_client.context()
    if context is None:
        print(f"Tenant has no ontology context. Create one with create_context(name='{CONTEXT_NAME}') first.")
        return 1
    context_name: str = context.context
    live_concepts, live_properties = fetch_live_state(ontology_client, context_name)
    print("-" * 120)
    print(f" Context '{context_name}' (base URI {context.base_uri}, version {context.version})")
    print(f" {len(live_concepts)} concept(s), {len(live_properties)} property(ies)")
    print("-" * 120)

    if args.export:
        args.export.write_text(ontology_client.rdf_export(context_name), encoding="utf-8")
        print(f"Live ontology written to '{args.export}'.")

    # ------------------------------- Compare with the RDF file --------------------------------------------------------
    target: Ontology = load_target_ontology(args.rdf)
    print(
        f"Target ontology '{args.rdf}': {len(target.classes)} concept(s), "
        f"{len(target.data_properties)} data property(ies), {len(target.object_properties)} object property(ies)"
    )
    plan: AlignmentPlan = build_plan(target, live_concepts, live_properties)
    print_plan(plan)

    if plan.is_empty:
        return 0
    if not args.apply:
        print("\nDry run: nothing was changed. Re-run with --apply to align the tenant.")
        return 0

    # ------------------------------- Align ----------------------------------------------------------------------------
    print("-" * 120)
    print(" Applying")
    print("-" * 120)
    summary: Summary = apply_plan(
        ontology_client, context_name, plan, set(live_concepts.keys()), set(live_properties.keys())
    )
    if summary.has_changes:
        publish(ontology_client, knowledge_client, context_name)
    else:
        print("No change reached the ontology, so there is nothing to commit.")
    print(
        f"Created {summary.created}, updated {summary.updated}, " f"skipped {summary.skipped}, failed {summary.failed}."
    )
    return 1 if summary.failed else 0


if __name__ == "__main__":
    sys.exit(main())
