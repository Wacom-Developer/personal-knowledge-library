# -*- coding: utf-8 -*-
# Copyright © 2021-2022 Wacom. All rights reserved.
import argparse
from typing import Optional, List

from knowledge.base.ontology import THING_CLASS
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.group import GroupManagementServiceAPI
from knowledge.services.users import UserManagementServiceAPI

DEMO_USER_EXTERNAL_USER_ID: str = 'ee6b0b0c-e51b-458c-909d-5ba7e81166e6'


if __name__ == '__main__':
    """
    REMARK:
    ------
    This script is deleting all entities, groups, and users. 
    Only the admin account will not be removed.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default="https://stage-private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()

    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Wacom Knowledge Listing", service_url=args.instance)
    # User Management
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=args.instance)

    # Group Management
    group_management: GroupManagementServiceAPI = GroupManagementServiceAPI(service_url=args.instance)

    admin_token, refresh_token, expiration_time = user_management.request_user_token(args.tenant, args.user)
    page_id: Optional[str] = None
    deleted_uris: int = 0

    while True:
        # pull
        entities, total_number, next_page_id = knowledge_client.listing(admin_token, THING_CLASS, page_id, limit=100)
        page_uris: List[str] = [e.uri for e in entities]
        pulled_entities: int = len(entities)
        if pulled_entities == 0:
            break
        # Not more than 100 entities are recommended
        knowledge_client.delete_entities(auth_key=admin_token, uris=page_uris, force=True)
        deleted_uris += len(page_uris)
        page_id = next_page_id
    print('-----------------------------------------------------------------------------------------------------------')
    print(f' Deleted a total number of {deleted_uris} entities.')
    print('-----------------------------------------------------------------------------------------------------------')
    for g in group_management.listing_groups(auth_key=admin_token, admin=True):
        print(f' Delete  group: {g.name}')
        group_management.delete_group(auth_key=admin_token, group_id=g.id)
    print('-----------------------------------------------------------------------------------------------------------')
    for u in user_management.listing_users(tenant_key=args.tenant, limit=1000):
        if u.external_user_id != args.user and u.external_user_id != DEMO_USER_EXTERNAL_USER_ID:
            print(f' Delete user: {u.external_user_id}')
            user_management.delete_user(tenant_key=args.tenant, external_id=u.external_user_id, internal_id=u.id)
    print('-----------------------------------------------------------------------------------------------------------')

