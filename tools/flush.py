# -*- coding: utf-8 -*-
# Copyright © 2021-24 Wacom. All rights reserved.
import argparse
from typing import Union, List

from knowledge.base.ontology import OntologyClassReference
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.session import PermanentSession

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user",
                        help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant",
                        help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-e", "--type",
                        help="IRI of entity type. wacom:core#Thing will find all entities.")
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()

    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Flush entities",
                                                                service_url=args.instance)
    session: PermanentSession = wacom_client.login(args.tenant, args.user)
    is_admin: bool = session.roles == "TenantAdmin"
    next_page_id: Union[str, None] = None
    deleted_uris: int = 0
    filter_type: OntologyClassReference = THING_OBJECT
    if args.type:
        filter_type = OntologyClassReference.parse(args.type)
    while True:
        # pull
        entities, total_number, next_page_id = wacom_client.listing(filter_type, next_page_id, limit=100)
        page_uris: List[str] = [e.uri for e in entities]
        pulled_entities: int = len(entities)
        if pulled_entities == 0:
            break
        # Not more than 100 entities are recommended
        try:
            wacom_client.delete_entities(uris=page_uris, force=True)
        except WacomServiceException as e:
            print(f'[Message]:={e.message}')
            print(f'[Status code]:={e.status_code}')
            print(f'[Service response]:={e.service_response}')

        deleted_uris += len(page_uris)
    print('-----------------------------------------------------------------------------------------------------------')
    print(f'Deleted a total number of {deleted_uris} entities.')
    print('-----------------------------------------------------------------------------------------------------------')
