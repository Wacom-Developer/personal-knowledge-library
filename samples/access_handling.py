# -*- coding: utf-8 -*-
# Copyright © 2021-24 Wacom Authors. All Rights Reserved.
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
from typing import List

from knowledge.base.entity import Label, Description
from knowledge.base.language import EN_US, DE_DE, JA_JP
from knowledge.base.ontology import OntologyClassReference, ThingObject
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.group import GroupManagementServiceAPI, Group
from knowledge.services.users import UserManagementServiceAPI

# ------------------------------- User credential ----------------------------------------------------------------------
TOPIC_CLASS: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Topic')


def create_entity() -> ThingObject:
    """Create a new entity.

    Returns
    -------
    entity: ThingObject
        Entity object
    """
    # Main labels for entity
    topic_labels: List[Label] = [
        Label('Hidden', EN_US),
        Label('Versteckt', DE_DE),
        Label('隠れた', JA_JP),
    ]

    # Topic description
    topic_description: List[Description] = [
        Description('Hidden entity to explain access management.', EN_US),
        Description('Verstecke Entität, um die Zugriffsteuerung zu erlären.', DE_DE)
    ]
    # Topic
    topic_object: ThingObject = ThingObject(label=topic_labels, concept_type=TOPIC_CLASS, description=topic_description)
    return topic_object


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
    # User Management
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=args.instance)
    # Group Management
    group_management: GroupManagementServiceAPI = GroupManagementServiceAPI(service_url=args.instance)
    admin_token, refresh_token, expiration_time = user_management.request_user_token(TENANT_KEY, EXTERNAL_USER_ID)
    # Now, we create a users
    u1, u1_token, _, _ = user_management.create_user(TENANT_KEY, "u1")
    u2, u2_token, _, _ = user_management.create_user(TENANT_KEY, "u2")
    u3, u3_token, _, _ = user_management.create_user(TENANT_KEY, "u3")

    # Now, let's create an entity
    thing: ThingObject = create_entity()
    entity_uri: str = knowledge_client.create_entity(thing, auth_key=u1_token)
    # Only user 1 can access the entity from cloud storage
    my_thing: ThingObject = knowledge_client.entity(entity_uri, auth_key=u1_token)
    print(f'User is the owner of {my_thing.owner}')
    # Now only user 1 has access to the personal entity
    knowledge_client.entity(u1_token, entity_uri)
    # Try to access the entity
    try:
        knowledge_client.entity(u2_token, entity_uri)
    except WacomServiceException as we:
        print(f"Expected exception as user 2 has no access to the personal entity of user 1. Exception: {we}")
        print(f"Status code: {we.status_code}")
        print(f"Response text: {we.service_response}")
    # Try to access the entity
    try:
        knowledge_client.entity(u3_token, entity_uri)
    except WacomServiceException as we:
        print(f"Expected exception as user 3 has no access to the personal entity of user 1. Exception: {we}")
    # Now, user 1 creates a group
    g: Group = group_management.create_group("test-group", auth_key=u1_token)
    # Shares the join key with user 2 and user 2 joins
    group_management.join_group(u2_token, g.id, g.join_key)
    # Share entity with group
    group_management.add_entity_to_group(u1_token, g.id, entity_uri)
    # Now, user 2 should have access
    other_thing: ThingObject = knowledge_client.entity(u2_token, entity_uri)
    print(f'User 2 is the owner of the thing: {other_thing.owner}')
    # Try to access the entity
    try:
        knowledge_client.entity(u3_token, entity_uri)
    except WacomServiceException as we:
        print(f"Expected exception as user 3 still has no access to the personal entity of user 1. Exception: {we}")
    # Un-share the entity
    group_management.remove_entity_to_group(u1_token, g.id, entity_uri)
    # Now, again no access
    try:
        knowledge_client.entity(u2_token, entity_uri)
    except WacomServiceException as we:
        print(f"Expected exception as user 2 has no access to the personal entity of user 1. Exception: {we}")
    group_management.leave_group(group_id=g.id, auth_key=u2_token)
    # Now, share the entity with the whole tenant
    my_thing.tenant_access_right.read = True
    knowledge_client.update_entity(my_thing, auth_key=u1_token)
    # Now, all users can access the entity
    knowledge_client.entity(u2_token, entity_uri)
    knowledge_client.entity(u3_token, entity_uri)
    # Finally, clean up
    knowledge_client.delete_entity(entity_uri, force=True, auth_key=u1_token)
    # Remove users
    user_management.delete_user(TENANT_KEY, u1.external_user_id, u1.id)
    user_management.delete_user(TENANT_KEY, u2.external_user_id, u2.id)
    user_management.delete_user(TENANT_KEY, u3.external_user_id, u3.id)
