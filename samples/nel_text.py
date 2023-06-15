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
from typing import List, Dict

import urllib3

from knowledge.base.entity import LanguageCode
from knowledge.base.ontology import OntologyPropertyReference, ThingObject, ObjectProperty
from knowledge.nel.base import KnowledgeGraphEntity
from knowledge.nel.engine import WacomEntityLinkingEngine
from knowledge.services.graph import WacomKnowledgeService

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LANGUAGE_CODE: LanguageCode = LanguageCode("en_US")
TEXT: str = "Leonardo da Vinci painted the Mona Lisa."


def print_entity(entity: KnowledgeGraphEntity, list_idx: int, auth_key: str, client: WacomKnowledgeService):
    """
    Printing entity details.

    Parameters
    ----------
    entity: KnowledgeGraphEntity
        Named entity
    list_idx: int
        Index with a list
    auth_key: str
        Authorization key
    client: WacomKnowledgeService
        Knowledge graph client
    """
    thing: ThingObject = knowledge_client.entity(auth_key=user_token, uri=entity.entity_source.uri)
    print(f'[{list_idx}] - {e.ref_text} [{e.start_idx}-{e.end_idx}] : {thing.uri} <{thing.concept_type.iri}>')
    if len(thing.label) > 0:
        print('    | [Labels]')
        for la in thing.label:
            print(f'    |     |- "{la.content}"@{la.language_code}')
        print('    |')
    if len(thing.label) > 0:
        print('    | [Alias]')
        for la in thing.alias:
            print(f'    |     |- "{la.content}"@{la.language_code}')
        print('    |')
    relations: Dict[OntologyPropertyReference, ObjectProperty] = client.relations(auth_key=auth_key, uri=thing.uri)
    if len(thing.data_properties) > 0:
        print('    | [Attributes]')
        for data_property, labels in thing.data_properties.items():
            print(f'    |    |- {data_property.iri}:')
            for li in labels:
                print(f'    |    |-- "{li.value}"@{li.language_code}')
        print('    |')
    if len(relations) > 0:
        print('    | [Relations]')
        for re in relations.values():
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
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom personal knowledge REST API Client
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Named Entity Linking Knowledge access",
        service_url=args.instance)
    #  Wacom Named Entity Linking
    nel_client: WacomEntityLinkingEngine = WacomEntityLinkingEngine(
        service_url=args.instance,
        service_endpoint=WacomEntityLinkingEngine.SERVICE_ENDPOINT
    )
    # Use special tenant for testing:  Unit-test tenant
    user_token, refresh_token, expiration_time = nel_client.request_user_token(TENANT_KEY, EXTERNAL_USER_ID)
    entities: List[KnowledgeGraphEntity] = nel_client.\
        link_personal_entities(auth_key=user_token, text=TEXT,
                               language_code=LANGUAGE_CODE)
    idx: int = 1
    print('-----------------------------------------------------------------------------------------------------------')
    print(f'Text: "{TEXT}"@{LANGUAGE_CODE}')
    print('-----------------------------------------------------------------------------------------------------------')
    for e in entities:
        print_entity(e, idx, user_token, knowledge_client)
        idx += 1
