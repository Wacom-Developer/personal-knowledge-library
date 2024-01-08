# -*- coding: utf-8 -*-
# Copyright © 2021-2024 Wacom. All rights reserved.
import argparse
from typing import Union, Dict

from knowledge.base.ontology import OntologyClassReference
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.session import PermanentSession
from knowledge.utils.graph import things_iter, count_things

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')


def print_summary(total: int, types: Dict[str, int], languages: Dict[str, int]):
    """
    Print summary of the listing.

    Parameters:
    -----------
    total: int
        Total number of entities.
    types: Dict[str, int]
        Dictionary of types and their counts.
    languages: Dict[str, int]
        Dictionary of languages and their counts.
    """
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
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-r", "--relations", action="store_true", help="Find all relations.")
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()

    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Wacom Knowledge Listing",
                                                                service_url=args.instance)
    session: PermanentSession = wacom_client.login(args.tenant, args.user)
    next_page_id: Union[str, None] = None
    page_number: int = 1
    entity_count: int = 0
    types_count: Dict[str, int] = {}
    languages_count: Dict[str, int] = {}
    total_number: int = count_things(wacom_client, session.auth_token, THING_OBJECT)
    for idx, (thing, auth_token, refresh_token) in enumerate(things_iter(wacom_client,
                                                                         session.auth_token, session.refresh_token,
                                                                         THING_OBJECT)):
            print(f'[{idx}] : {thing}')
            wacom_client.entity(thing.uri)
            # Pull relations if configured
            if args.relations:
                relations = wacom_client.relations(uri=thing.uri)
                thing.object_properties = relations
                for re in relations.values():
                    print(f' |- {re.relation.iri}: [Incoming]: {re.incoming_relations} |'
                          f' [Outgoing] : {re.outgoing_relations}')
            if thing.concept_type.iri not in types_count:
                types_count[thing.concept_type.iri] = 0
            types_count[thing.concept_type.iri] += 1
            for label in thing.label:
                if label.language_code not in languages_count:
                    languages_count[label.language_code] = 0
                languages_count[label.language_code] += 1
            idx += 1

    print_summary(total_number, types_count, languages_count)

