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
import argparse
import sys
from typing import Optional, List

from knowledge.base.entity import Label, Description
from knowledge.base.language import EN_US, DE_DE
from knowledge.base.ontology import (
    DataPropertyType,
    OntologyClassReference,
    OntologyPropertyReference,
    ThingObject,
    DataProperty,
    OntologyContext,
)
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.session import PermanentSession

# ------------------------------- Constants ----------------------------------------------------------------------------
LEONARDO_DA_VINCI: str = "Leonardo da Vinci"
CONTEXT_NAME: str = "core"
# Wacom Base Ontology Types
PERSON_TYPE: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")
# Demo Class
ARTIST_TYPE: OntologyClassReference = OntologyClassReference.parse("demo:creative#Artist")
# Demo Object property
IS_INSPIRED_BY: OntologyPropertyReference = OntologyPropertyReference.parse("demo:creative#isInspiredBy")
# Demo Data property
STAGE_NAME: OntologyPropertyReference = OntologyPropertyReference.parse("demo:creative#stageName")


def create_artist() -> ThingObject:
    """
    Create a new artist entity.
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

    data_property: DataProperty = DataProperty(content="Salaj", property_ref=STAGE_NAME, language_code=EN_US)
    # Topic
    artist: ThingObject = ThingObject(label=topic_labels, concept_type=ARTIST_TYPE, description=topic_description)
    artist.add_data_property(data_property)
    return artist


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
    if session.roles != "TenantAdmin":
        print(f"User {EXTERNAL_USER_ID} is not an admin user.")
        sys.exit(1)
    knowledge_client.use_session(session.id)
    knowledge_client.ontology_update()
    context: Optional[OntologyContext] = ontology_client.context()
    if context is None:
        # First, create a context for the ontology
        ontology_client.create_context(name=CONTEXT_NAME, base_uri=f"demo:{CONTEXT_NAME}")
        context_name: str = CONTEXT_NAME
    else:
        context_name: str = context.context
    # Creating a class which is a subclass of a person
    ontology_client.create_concept(context_name, reference=ARTIST_TYPE, subclass_of=PERSON_TYPE)

    # Object properties
    ontology_client.create_object_property(
        context=context_name,
        reference=IS_INSPIRED_BY,
        domains_cls=[ARTIST_TYPE],
        ranges_cls=[PERSON_TYPE],
        inverse_of=None,
        subproperty_of=None,
    )
    # Data properties
    ontology_client.create_data_property(
        context=context_name,
        reference=STAGE_NAME,
        domains_cls=[ARTIST_TYPE],
        ranges_cls=[DataPropertyType.STRING],
        subproperty_of=None,
    )
    # Commit the changes of the ontology. This is very important to confirm changes.
    ontology_client.commit(context=context_name)
    # Trigger graph service. After the update the ontology is available and the new entities can be created
    knowledge_client.ontology_update()

    res_entities, next_search_page = knowledge_client.search_labels(
        search_term=LEONARDO_DA_VINCI, language_code=EN_US, limit=1000
    )
    leo: Optional[ThingObject] = None
    for entity in res_entities:
        #  Entities must be a person and the label match with full string
        if entity.concept_type == PERSON_TYPE and LEONARDO_DA_VINCI in [la.content for la in entity.label]:
            leo = entity
            break

    artist_student: ThingObject = create_artist()
    artist_student_uri: str = knowledge_client.create_entity(artist_student)
    knowledge_client.create_relation(artist_student_uri, IS_INSPIRED_BY, leo.uri)
