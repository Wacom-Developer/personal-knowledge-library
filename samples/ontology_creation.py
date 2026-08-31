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
Extending the ontology and using the new types
==============================================

Walks the full edit-commit-apply cycle of the ontology service and then uses the new
types in the knowledge graph:

1. Read the tenant's ontology context.
2. Create a concept class, a data property, and a pair of mutually inverse object
   properties.
3. Review the uncommitted changes (`pending_version`) and what the tenant has added on
   top of the base ontology (`context_diff`).
4. Commit the ontology, apply it to the graph, and wait for the apply to finish.
5. Create an entity of the new class and relate it through the new object property.

Requires a shadow user with the **TenantAdmin** role; ordinary users may read the
ontology but not change it.

Usage
-----
>>> python ontology_creation.py -t <tenant-api-key> -u <external-user-id>
"""

import argparse
import sys
import time
from typing import List, Optional

from knowledge.base.entity import Label, Description
from knowledge.base.language import EN_US, DE_DE
from knowledge.base.ontology import (
    DataProperty,
    DataPropertyType,
    ObjectProperty,
    OntologyClassReference,
    OntologyContext,
    OntologyDiff,
    OntologyPropertyReference,
    OntologyUpdateStatus,
    PendingOntologyVersion,
    ThingObject,
)
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.session import PermanentSession

# ------------------------------- Constants ----------------------------------------------------------------------------
LEONARDO_DA_VINCI: str = "Leonardo da Vinci"
CONTEXT_NAME: str = "core"
ADMIN_ROLE: str = "TenantAdmin"

# Wacom base ontology type. Base concepts and properties are read-only: the service answers
# 403 to any attempt to change or delete them.
PERSON_TYPE: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")

# Local names of the types this sample adds. They are resolved against the base URI of the
# tenant's own context, because a concept has to live inside it.
ARTIST_NAME: str = "Artist"
STAGE_NAME_NAME: str = "stageName"
IS_INSPIRED_BY_NAME: str = "isInspiredBy"
INSPIRED_NAME: str = "inspired"

REQUIRED_IDLE_POLLS: int = 2
"""Consecutive idle readings needed before an apply counts as finished."""


def create_artist(artist_type: OntologyClassReference, stage_name: OntologyPropertyReference) -> ThingObject:
    """
    Create a new artist entity.

    Parameters
    ----------
    artist_type: OntologyClassReference
        Concept class of the entity.
    stage_name: OntologyPropertyReference
        Data property holding the stage name.

    Returns
    -------
    instance: ThingObject
        Artist entity
    """
    # Main labels for entity
    topic_labels: List[Label] = [
        Label("Gian Giacomo Caprotti", EN_US),
    ]

    # Topic description
    topic_description: List[Description] = [
        Description("Hidden entity to explain access management.", EN_US),
        Description("Verstecke Entität, um die Zugriffsteuerung zu erlären.", DE_DE),
    ]

    data_property: DataProperty = DataProperty(content="Salaj", property_ref=stage_name, language_code=EN_US)
    # Topic
    artist: ThingObject = ThingObject(label=topic_labels, concept_type=artist_type, description=topic_description)
    artist.add_data_property(data_property)
    return artist


def wait_until_applied(client: WacomKnowledgeService, attempts: int = 30, delay: float = 2.0) -> None:
    """Wait until the tenant's ontology update has finished.

    `ontology_update` only **accepts** the apply; the work continues in the background
    while the tenant is locked, and every graph write is rejected until it completes.

    **Remark:**
    The service reports 'NoUpdateInProgress' both when an apply has completed and when
    none was ever started. A single idle reading would therefore return before a
    just-triggered apply registers, so two consecutive idle readings are required.

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument(
        "-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom Ontology REST API Client
    ontology_client: OntologyService = OntologyService(service_url=args.instance)
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Ontology Creation Demo", service_url=args.instance
    )
    # Login as admin user
    session: PermanentSession = ontology_client.login(TENANT_KEY, EXTERNAL_USER_ID)
    if ADMIN_ROLE not in session.roles:
        print(f"User {EXTERNAL_USER_ID} is not an admin user.")
        sys.exit(1)
    # Each client keeps its own session table, so use_session cannot resolve a session id
    # minted by another client. Hand the token over instead.
    knowledge_client.register_token(auth_key=session.auth_token, refresh_token=session.refresh_token)

    # ------------------------------- Context ------------------------------------------------------------------------
    context: Optional[OntologyContext] = ontology_client.context()
    if context is None:
        # The tenant has no ontology context yet; create one.
        ontology_client.create_context(name=CONTEXT_NAME, base_uri=f"wacom:{CONTEXT_NAME}")
        context = ontology_client.context()
    context_name: str = context.context
    print(f"Context: {context_name} (base URI {context.base_uri}, version {context.version})")

    # New types must live under the base URI of the context that owns them.
    ARTIST_TYPE: OntologyClassReference = OntologyClassReference.parse(f"{context.base_uri}{ARTIST_NAME}")
    STAGE_NAME: OntologyPropertyReference = OntologyPropertyReference.parse(f"{context.base_uri}{STAGE_NAME_NAME}")
    IS_INSPIRED_BY: OntologyPropertyReference = OntologyPropertyReference.parse(
        f"{context.base_uri}{IS_INSPIRED_BY_NAME}"
    )
    INSPIRED: OntologyPropertyReference = OntologyPropertyReference.parse(f"{context.base_uri}{INSPIRED_NAME}")

    # ------------------------------- Ontology changes ---------------------------------------------------------------
    # Creating a class which is a subclass of a person
    ontology_client.create_concept(context_name, reference=ARTIST_TYPE, subclass_of=PERSON_TYPE)

    # Data property. A literal property takes exactly one XSD data type as its range and
    # must not declare an inverse.
    ontology_client.create_data_property(
        context=context_name,
        reference=STAGE_NAME,
        domains_cls=[ARTIST_TYPE],
        ranges_cls=[DataPropertyType.STRING],
        subproperty_of=None,
    )
    # Object properties. Declaring the second one as the inverse of the first makes the
    # service maintain the pair: it also records isInspiredBy as the inverse of inspired.
    ontology_client.create_object_property(
        context=context_name,
        reference=IS_INSPIRED_BY,
        domains_cls=[ARTIST_TYPE],
        ranges_cls=[PERSON_TYPE],
        inverse_of=None,
        subproperty_of=None,
    )
    ontology_client.create_object_property(
        context=context_name,
        reference=INSPIRED,
        domains_cls=[PERSON_TYPE],
        ranges_cls=[ARTIST_TYPE],
        inverse_of=IS_INSPIRED_BY,
        subproperty_of=None,
    )

    # ------------------------------- Review before committing -------------------------------------------------------
    # The pending version is the change log a commit would turn into the next version.
    pending_version: PendingOntologyVersion = ontology_client.pending_version(context_name)
    print(f"Pending version {pending_version.version} with {len(pending_version.changes)} change(s):")
    for change in pending_version.changes:
        print(f"  {change.operation} {change.element_kind} -> {change.element_uri}")

    # ------------------------------- Commit and apply ---------------------------------------------------------------
    # Committing persists the schema change on the ontology side only.
    ontology_client.commit(context=context_name)
    wait_until_committed(ontology_client, context_name)
    # Applying it makes the graph service respect the new version. The call returns as soon
    # as the apply is accepted, so wait for it before writing entities.
    knowledge_client.ontology_update()
    wait_until_applied(knowledge_client)

    # The diff reports everything the tenant added on top of the base ontology - which is
    # also everything a reset_context would destroy.
    diff: OntologyDiff = ontology_client.context_diff(context_name)
    print(f"Tenant added {len(diff.added_concepts)} concept(s) and {len(diff.added_properties)} property(ies).")

    # ------------------------------- Using the new types ------------------------------------------------------------
    res_entities, next_search_page = knowledge_client.search_labels(
        search_term=LEONARDO_DA_VINCI, language_code=EN_US, limit=1000
    )
    leo: Optional[ThingObject] = None
    for entity in res_entities:
        #  Entities must be a person and the label matches with full string
        if entity.concept_type == PERSON_TYPE and LEONARDO_DA_VINCI in [la.content for la in entity.label]:
            leo = entity
            break
    if leo is None:
        print(f"No person labelled '{LEONARDO_DA_VINCI}' found; nothing to relate the artist to.")
        sys.exit(1)

    artist_student: ThingObject = create_artist(ARTIST_TYPE, STAGE_NAME)
    artist_student_uri: str = knowledge_client.create_entity(artist_student)
    # One call is enough: because isInspiredBy and inspired are declared inverse, the
    # service also records the reciprocal edge. Creating it explicitly would be rejected
    # with '409 The relation already exists'.
    knowledge_client.create_relation(artist_student_uri, IS_INSPIRED_BY, leo.uri)

    # Relations come back as entity objects rather than bare URIs, so compare on the URIs.
    relations = knowledge_client.relations(leo.uri)
    inspired_relation: Optional[ObjectProperty] = relations.get(INSPIRED)
    if inspired_relation is not None and artist_student_uri in inspired_relation.outgoing_uris:
        print(f"The service materialized the inverse: {leo.uri} --{INSPIRED.iri}--> {artist_student_uri}")
