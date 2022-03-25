# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
import argparse
from typing import List, Dict, Optional

import urllib3

from knowledge.base.ontology import OntologyClassReference, ThingObject

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from knowledge.services.graph import WacomKnowledgeService

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')


def print_summary(total: int, types: Dict[str, int], languages: Dict[str, int]):
    print('---------------------------------------------------------------------------------------------------')
    print(f' Total number: {total}')
    print('---------------------------------------------------------------------------------------------------')
    print('Concept Types:')
    for c_type, count in types.items():
        print(f' {c_type}: {count}')
    print('---------------------------------------------------------------------------------------------------')
    print('LocalizedContent Languages:')
    for language_code, count in languages.items():
        print(f' {language_code}: {count}')
    print('---------------------------------------------------------------------------------------------------')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="User")
    parser.add_argument("-t", "--tenant", help="Tenant")
    parser.add_argument("-r", "--relations", action="store_true", help="Find all relations.")
    args = parser.parse_args()

    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Wacom Knowledge Listing",
        service_url='https://private-knowledge.wacom.com')
    user_auth_key: str = wacom_client.request_user_token(args.tenant, args.user)
    page_id: Optional[str] = None
    page_number: int = 1
    entity_count: int = 0
    types_count: Dict[str, int] = {}
    languages_count: Dict[str, int] = {}
    dump_entities: List[ThingObject] = []
    idx: int = 1
    while True:
        # pull
        entities, total_number, next_page_id = wacom_client.listing(user_auth_key, THING_OBJECT, page_id=page_id,
                                                                    limit=100)
        pulled_entities: int = len(entities)
        entity_count += pulled_entities
        print('---------------------------------------------------------------------------------------------------')
        print(f' Page: {page_number} Number of entities: {len(entities)}  ({entity_count}/{total_number}) '
              f'Next page id: {next_page_id}')
        print('---------------------------------------------------------------------------------------------------')
        for e in entities:
            print(f'[{idx}] : {e}')
            wacom_client.entity(user_auth_key, e.uri)
            # Pull relations if configured
            if args.relations:
                relations = wacom_client.relations(auth_key=user_auth_key, uri=e.uri)
                e.object_properties = relations
                for re in relations.values():
                    print(f' |- {re.relation.iri}: [Incoming]: {re.incoming_relations} |'
                          f' [Outgoing] : {re.outgoing_relations}')
            if e.concept_type.iri not in types_count:
                types_count[e.concept_type.iri] = 0
            types_count[e.concept_type.iri] += 1
            for label in e.label:
                if label.language_code not in languages_count:
                    languages_count[label.language_code] = 0
                languages_count[label.language_code] += 1
            idx += 1

        if pulled_entities == 0:
            print_summary(total_number, types_count, languages_count)
            break
        page_number += 1
        page_id = next_page_id


