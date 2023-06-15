# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom Authors. All Rights Reserved.
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
from typing import Optional

from knowledge.base.entity import LanguageCode, Description, Label
from knowledge.base.ontology import OntologyClassReference, OntologyPropertyReference, ThingObject, ObjectProperty
from knowledge.services.graph import WacomKnowledgeService

# ------------------------------- Knowledge entities -------------------------------------------------------------------
LEONARDO_DA_VINCI: str = 'Leonardo da Vinci'
SELF_PORTRAIT_STYLE: str = 'self-portrait'
ICON: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Mona_Lisa_%28copy%2C_Thalwil%2C_Switzerland%29."\
            "JPG/1024px-Mona_Lisa_%28copy%2C_Thalwil%2C_Switzerland%29.JPG"
# ------------------------------- Ontology class names -----------------------------------------------------------------
THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')
"""
The Ontology will contain a Thing class where is the root class in the hierarchy. 
"""
ARTWORK_CLASS: OntologyClassReference = OntologyClassReference('wacom', 'creative', 'VisualArtwork')
PERSON_CLASS: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Person')
ART_STYLE_CLASS: OntologyClassReference = OntologyClassReference.parse('wacom:creative#ArtStyle')
IS_CREATOR: OntologyPropertyReference = OntologyPropertyReference('wacom', 'core', 'created')
HAS_TOPIC: OntologyPropertyReference = OntologyPropertyReference.parse('wacom:core#hasTopic')
CREATED: OntologyPropertyReference = OntologyPropertyReference.parse('wacom:core#created')
HAS_ART_STYLE: OntologyPropertyReference = OntologyPropertyReference.parse('wacom:creative#hasArtstyle')


def print_entity(entity: ThingObject, list_idx: int, auth_key: str, client: WacomKnowledgeService,
                 short: bool = False):
    """
    Printing entity details.

    Parameters
    ----------
    entity: ThingObject
        Entity with properties
    list_idx: int
        Index with a list
    auth_key: str
        Authorization key
    client: WacomKnowledgeService
        Knowledge graph client
    short: bool
        Short summary
    """
    print(f'[{list_idx}] : {print_entity.uri} <{entity.concept_type.iri}>')
    if len(entity.label) > 0:
        print('    | [Labels]')
        for la in entity.label:
            print(f'    |     |- "{la.content}"@{la.language_code}')
        print('    |')
    if not short:
        if len(entity.alias) > 0:
            print('    | [Alias]')
            for la in entity.alias:
                print(f'    |     |- "{la.content}"@{la.language_code}')
            print('    |')
        if len(entity.data_properties) > 0:
            print('    | [Attributes]')
            for data_property, labels in entity.data_properties.items():
                print(f'    |    |- {data_property.iri}:')
                for li in labels:
                    print(f'    |    |-- "{li.value}"@{li.language_code}')
            print('    |')

        relations_obj: dict[OntologyPropertyReference, ObjectProperty] = client.relations(auth_key=auth_key,
                                                                                          uri=entity.uri)
        if len(relations_obj) > 0:
            print('    | [Relations]')
            for re in relations_obj.values():
                print(f'    |--- {re.relation.iri}: ')
                print(f'           |- [Incoming]: {re.incoming_relations} ')
                print(f'           |- [Outgoing]: {re.outgoing_relations}')
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom personal knowledge REST API Client
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Wacom Knowledge Listing",
                                                                    service_url=args.instance)
    # Use special tenant for testing:  Unit-test tenant
    user_token, refresh_token, expiration_time = knowledge_client.request_user_token(TENANT_KEY, EXTERNAL_USER_ID)
    page_id: Optional[str] = None
    page_number: int = 1
    entity_count: int = 0
    print('-----------------------------------------------------------------------------------------------------------')
    print(' First step: Find Leonardo da Vinci in the knowledge graph.')
    print('-----------------------------------------------------------------------------------------------------------')
    res_entities, next_search_page = knowledge_client.search_labels(auth_key=user_token, search_term=LEONARDO_DA_VINCI,
                                                                    language_code=LanguageCode('en_US'), limit=1000)
    leo: Optional[ThingObject] = None
    s_idx: int = 1
    for entity in res_entities:
        #  Entity must be a person and the label match with full string
        if entity.concept_type == PERSON_CLASS and LEONARDO_DA_VINCI in [l.content for l in entity.label]:
            leo = entity
            break

    print('-----------------------------------------------------------------------------------------------------------')
    print(' What artwork exists in the knowledge graph.')
    print('-----------------------------------------------------------------------------------------------------------')
    relations_dict: dict[OntologyPropertyReference, ObjectProperty] = knowledge_client.relations(auth_key=user_token,
                                                                                                 uri=leo.uri)
    print(f' Artwork of {leo.label}')
    print('-----------------------------------------------------------------------------------------------------------')
    idx: int = 1
    if CREATED in relations_dict:
        for e in relations_dict[CREATED].outgoing_relations:
            print(f' [{idx}] {e.uri}: {e.label}')
            idx += 1
    print('-----------------------------------------------------------------------------------------------------------')
    print(' Let us create a new piece of artwork.')
    print('-----------------------------------------------------------------------------------------------------------')

    # Main labels for entity
    artwork_labels: list[Label] = [
        Label('Ginevra Gherardini', LanguageCode('en_US')),
        Label('Ginevra Gherardini', LanguageCode('de_DE'))
    ]
    # Alias labels for entity
    artwork_alias: list[Label] = [
        Label("Ginevra", LanguageCode('en_US')),
        Label("Ginevra", LanguageCode('de_DE'))
    ]
    # Topic description
    artwork_description: list[Description] = [
        Description('Oil painting of Mona Lisa\' sister', LanguageCode('en_US')),
        Description('Ölgemälde von Mona Lisa\' Schwester', LanguageCode('de_DE'))
    ]
    # Topic
    artwork_object: ThingObject = ThingObject(label=artwork_labels, concept_type=ARTWORK_CLASS,
                                              description=artwork_description,
                                              icon=ICON)
    artwork_object.alias = artwork_alias
    print(f' Create: {artwork_object}')
    # Create artwork
    artwork_entity_uri: str = knowledge_client.create_entity(user_token, artwork_object)
    print(f' Entity URI: {artwork_entity_uri}')
    # Create relation between Leonardo da Vinci and artwork
    knowledge_client.create_relation(auth_key=user_token, source=leo.uri, relation=IS_CREATOR,
                                     target=artwork_entity_uri)

    relations_dict = knowledge_client.relations(auth_key=user_token, uri=artwork_entity_uri)
    for ontology_property, object_property in relations_dict.items():
        print(f'  {object_property}')
    # You will see that wacom:core#isCreatedBy is automatically inferred as relation as it is the inverse property of
    # wacom:core#created.

    # Now, more search options
    res_entities, next_search_page = knowledge_client.search_description(user_token, 'Michelangelo\'s Sistine Chapel',
                                                                         LanguageCode('en_US'), limit=1000)
    print('-----------------------------------------------------------------------------------------------------------')
    print(' Search results.  Description: "Michelangelo\'s Sistine Chapel"')
    print('-----------------------------------------------------------------------------------------------------------')
    s_idx: int = 1
    for e in res_entities:
        print_entity(e, s_idx, user_token, knowledge_client)

    # Now, let's search all artwork that has the art style self-portrait
    res_entities, next_search_page = knowledge_client.search_labels(auth_key=user_token,
                                                                    search_term=SELF_PORTRAIT_STYLE,
                                                                    language_code=LanguageCode('en_US'), limit=1000)
    art_style: Optional[ThingObject] = None
    s_idx: int = 1
    for entity in res_entities:
        #  Entity must be a person and the label match with full string
        if entity.concept_type == ART_STYLE_CLASS and SELF_PORTRAIT_STYLE in [l.content for l in entity.label]:
            art_style = entity
            break
    res_entities, next_search_page = knowledge_client.search_relation(auth_key=user_token,
                                                                      subject_uri=None,
                                                                      relation=HAS_ART_STYLE,
                                                                      object_uri=art_style.uri,
                                                                      language_code=LanguageCode('en_US'))
    print('-----------------------------------------------------------------------------------------------------------')
    print(' Search results.  Relation: relation:=has_topic  object_uri:= unknown')
    print('-----------------------------------------------------------------------------------------------------------')
    s_idx: int = 1
    for e in res_entities:
        print_entity(e, s_idx, user_token, knowledge_client, short=True)
        s_idx += 1

    # Finally, the activation function retrieving the related identities to a pre-defined depth.
    entities, relations = knowledge_client.activations(auth_key=user_token,
                                                       uris=[leo.uri],
                                                       depth=1)
    print('-----------------------------------------------------------------------------------------------------------')
    print(f'Activation.  URI: {leo.uri}')
    print('-----------------------------------------------------------------------------------------------------------')
    s_idx: int = 1
    for e in res_entities:
        print_entity(e, s_idx, user_token, knowledge_client)
        s_idx += 1
    # All relations
    print('-----------------------------------------------------------------------------------------------------------')
    for r in relations:
        print(f'Subject: {r[0]} Predicate: {r[1]} Object: {r[2]}')
    print('-----------------------------------------------------------------------------------------------------------')
    page_id = None

    # Listing all entities which have the type
    idx: int = 1
    while True:
        # pull
        entities, total_number, next_page_id = knowledge_client.listing(user_token, ART_STYLE_CLASS, page_id=page_id,
                                                                        limit=100)
        pulled_entities: int = len(entities)
        entity_count += pulled_entities
        print('-------------------------------------------------------------------------------------------------------')
        print(f' Page: {page_number} Number of entities: {len(entities)}  ({entity_count}/{total_number}) '
              f'Next page id: {next_page_id}')
        print('-------------------------------------------------------------------------------------------------------')
        for e in entities:
            print_entity(e, idx, user_token, knowledge_client)
            idx += 1
        if pulled_entities == 0:
            break
        page_number += 1
        page_id = next_page_id
    print()
    # Delete all personal entities for this user
    while True:
        # pull
        entities, total_number, next_page_id = knowledge_client.listing(user_token, THING_OBJECT, page_id=page_id,
                                                                        limit=100)
        pulled_entities: int = len(entities)
        if pulled_entities == 0:
            break
        delete_uris: list[str] = [e.uri for e in entities]
        print(f'Cleanup. Delete entities: {delete_uris}')
        knowledge_client.delete_entities(auth_key=user_token, uris=delete_uris, force=True)
        page_number += 1
        page_id = next_page_id
    print('-----------------------------------------------------------------------------------------------------------')
