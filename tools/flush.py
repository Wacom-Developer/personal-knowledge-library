# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
import argparse
from typing import Optional, List

from knowledge.base.ontology import OntologyClassReference
from knowledge.services.graph import WacomKnowledgeService

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-e", "--type", help="IRI of entity type. wacom:core#Thing will find all entities.")
    parser.add_argument("-i", "--instance", default='https://stage-private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()

    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Flush entities",
                                                                service_url=args.instance)
    user_auth_key, refresh_token, expiration_time = wacom_client.request_user_token(args.tenant, args.user)
    page_id: Optional[str] = None
    deleted_uris: int = 0
    filter_type: OntologyClassReference = THING_OBJECT
    if args.type:
        filter_type = OntologyClassReference.parse(args.type)
    while True:
        # pull
        entities, total_number, next_page_id = wacom_client.listing(user_auth_key, filter_type, page_id, limit=100)
        page_uris: List[str] = [e.uri for e in entities]
        pulled_entities: int = len(entities)
        if pulled_entities == 0:
            break
        # Not more than 100 entities are recommended
        wacom_client.delete_entities(auth_key=user_auth_key, uris=page_uris, force=True)
        deleted_uris += len(page_uris)
        page_id = next_page_id
    print('-----------------------------------------------------------------------------------------------------------')
    print(f'Deleted a total number of {deleted_uris} entities.')
    print('-----------------------------------------------------------------------------------------------------------')
