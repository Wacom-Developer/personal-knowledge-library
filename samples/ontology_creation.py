# -*- coding: utf-8 -*-
# Copyright © 2021-2022 Wacom Authors. All Rights Reserved.
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
from typing import List, Optional

from knowledge.base.entity import OntologyContext, Label, LanguageCode, Description
from knowledge.base.ontology import DataPropertyType, OntologyClassReference, OntologyPropertyReference, ThingObject, \
    DataProperty
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService

# ------------------------------- Constants ----------------------------------------------------------------------------
LEONARDO_DA_VINCI: str = 'Leonardo da Vinci'
CONTEXT_NAME: str = 'core'
# Wacom Base Ontology Types
PERSON_TYPE: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")
# Demo Class
ARTIST_TYPE: OntologyClassReference = OntologyClassReference.parse("demo:creative#Artist")
# Demo Object property
IS_INSPIRED_BY: OntologyPropertyReference = OntologyPropertyReference.parse("demo:creative#isInspiredBy")
# Demo Data property
STAGE_NAME: OntologyPropertyReference = OntologyPropertyReference.parse("demo:creative#stageName")


def create_artist() -> ThingObject:
    # Main labels for entity
    topic_labels: List[Label] = [
        Label('Gian Giacomo Caprotti', LanguageCode('en_US'))
    ]

    # Topic description
    topic_description: List[Description] = [
        Description('Hidden entity to explain access management.', LanguageCode('en_US')),
        Description('Verstecke Entität, um die Zugriffsteuerung zu erlären.', LanguageCode('de_DE'))
    ]

    data_property: DataProperty = DataProperty(content='Salaj',
                                               property_ref=STAGE_NAME,
                                               language_code=LanguageCode('en_US'))
    # Topic
    artist: ThingObject = ThingObject(label=topic_labels, concept_type=ARTIST_TYPE, description=topic_description)
    artist.add_data_property(data_property)
    return artist


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default="https://stage-private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom Ontology REST API Client
    ontology_client: OntologyService = OntologyService(service_url=args.instance)
    admin_token: str = ontology_client.request_user_token(TENANT_KEY, EXTERNAL_USER_ID)
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Ontology Creation Demo",
        service_url=args.instance)
    contexts: List[OntologyContext] = ontology_client.contexts(admin_token)
    if len(contexts) == 0:
        # First, create a context for the ontology
        ontology_client.create_context(admin_token, name=CONTEXT_NAME, base_uri=f'demo:{CONTEXT_NAME}')
        context_name: str = CONTEXT_NAME
    else:
        context_name: str = contexts[0].context
    # Creating a class which is a subclass of a person
    ontology_client.create_concept(admin_token, CONTEXT_NAME, reference=ARTIST_TYPE, subclass_of=PERSON_TYPE)

    # Object properties
    ontology_client.create_object_property(auth_key=admin_token, context=CONTEXT_NAME,
                                           reference=IS_INSPIRED_BY, domain_cls=ARTIST_TYPE, range_cls=PERSON_TYPE,
                                           inverse_of=None, subproperty_of=None)
    # Data properties
    ontology_client.create_data_property(auth_key=admin_token, context=CONTEXT_NAME,
                                         reference=STAGE_NAME,
                                         domain_cls=ARTIST_TYPE,
                                         range_cls=DataPropertyType.STRING,
                                         subproperty_of=None)

    # Commit the changes of the ontology. This is very important to confirm changes.
    ontology_client.commit(admin_token, CONTEXT_NAME)
    # Trigger graph updater. After the update the ontology is available and the new entities can be created
    knowledge_client.ontology_update(admin_token)

    res_entities, next_search_page = knowledge_client.search_labels(auth_key=admin_token, search_term=LEONARDO_DA_VINCI,
                                                                    language_code=LanguageCode('en_US'), limit=1000)
    leo: Optional[ThingObject] = None
    for entity in res_entities:
        #  Entity must be a person and the label match with full string
        if entity.concept_type == PERSON_TYPE and LEONARDO_DA_VINCI in [la.content for la in entity.label]:
            leo = entity
            break

    artist_student: ThingObject = create_artist()
    artist_student_uri: str = knowledge_client.create_entity(admin_token, artist_student)
    knowledge_client.create_relation(admin_token, artist_student_uri, IS_INSPIRED_BY, leo.uri)
