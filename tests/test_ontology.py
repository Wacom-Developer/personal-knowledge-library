# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom. All rights reserved.
import os
from typing import List, Optional
from unittest import TestCase

from knowledge.base.ontology import OntologyContext, ontology_import, Ontology
from knowledge.services.ontology import OntologyService
from knowledge.services.session import Session
from knowledge.services.users import UserManagementServiceAPI, User, UserRole


class OntologyFlow(TestCase):
    """
    Testing
    """
    # -----------------------------------------------------------------------------------------------------------------
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=os.environ.get('INSTANCE'),
                                                                         service_endpoint="graph/v1")
    ontology: OntologyService = OntologyService(service_url=os.environ.get('INSTANCE'),
                                                service_endpoint="ontology/v1")

    '''User management service.'''
    tenant_api_key: str = os.environ.get('TENANT_API_KEY')
    LIMIT: int = 10000

    def test_1_ontology(self):
        list_user_all: List[User] = self.user_management.listing_users(self.tenant_api_key)
        admin_external_user: Optional[str] = None
        for u_i in list_user_all:
            if UserRole.ADMIN in u_i.user_roles:
                admin_external_user = u_i.external_user_id
        self.assertIsNotNone(admin_external_user)
        session: Session = self.user_management.login(self.tenant_api_key, admin_external_user)
        context: Optional[OntologyContext] = self.ontology.context(session.auth_token)
        self.assertIsNotNone(context)
        rdf: str = self.ontology.rdf_export(session.auth_token, context.context)
        self.assertIsNotNone(rdf)
        ontology: Ontology = ontology_import(rdf, session.tenant_id, context.context)
        self.assertIsNotNone(ontology)

