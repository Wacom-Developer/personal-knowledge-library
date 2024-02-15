# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom. All rights reserved.
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from knowledge.base.ontology import OntologyContext
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.session import PermanentSession
from knowledge.services.users import UserManagementServiceAPI, User, UserRole

ROLE_MAPPING: Dict[str, UserRole] = {role.value.lower(): role for role in UserRole}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file for tenant creation.", required=True, type=Path)
    args = parser.parse_args()
    if not args.input.exists():
        print(f"Input file {args.input} does not exist.")
        sys.exit(1)
    with args.input.open('r') as fp:
        configuration: Dict[str, Any] = json.load(fp)
        service_url: str = configuration['service']['url']
        tenant_api_key: str = configuration['tenant']['api_key']
        # First phase: Create users that are not yet existing
        user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=service_url)
        external_user_ids: Dict[str, User] = {}
        admin_external_user: Optional[str] = None
        # First, get all existing users
        for user in user_management.listing_users(tenant_api_key, offset=0, limit=1000):
            external_user_ids[user.external_user_id] = user
        # Create users that are not yet existing
        for user in configuration['users']:
            external_user_id: str = user['external_id']
            role: UserRole = ROLE_MAPPING[user['role'].lower()]
            if role == UserRole.ADMIN:
                admin_external_user = external_user_id
            if external_user_id not in external_user_ids:
                user_management.create_user(tenant_key=tenant_api_key, external_id=external_user_id,
                                            meta_data=user['meta_data'],
                                            roles=[role])

        if not admin_external_user:
            print("No admin user found.")
            sys.exit(1)
        # Second phase: Create the ontology
        context_name: str = configuration['ontology']['context']
        schema: str = configuration['ontology']['schema']
        ontology_client: OntologyService = OntologyService(service_url=service_url)
        knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
            application_name="Ontology Creation",
            service_url=service_url)
        session: PermanentSession = ontology_client.login(tenant_api_key, admin_external_user)
        knowledge_client.use_session(session.id)
        context: Optional[OntologyContext] = ontology_client.context()
        # Check if the context already exists
        if not context:
            # First, create a context for the ontology
            ontology_client.create_context(name=context_name,
                                           base_uri=f'{schema}:{context_name}#')
            context: Optional[OntologyContext] = ontology_client.context()
        # If there is no version defined context, we need to commit the ontology
        if context.version is None:
            # Commit the changes of the ontology. This is very important to confirm changes.
            ontology_client.commit(context_name)
            # Trigger graph service. After the update the ontology is available and the new entities can be created
            knowledge_client.ontology_update()
