# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom. All rights reserved.
import os
from typing import List, Optional
from unittest import TestCase

from knowledge.base.ontology import OntologyContext, ontology_import, Ontology, OntologyClass, OntologyProperty
from knowledge.services.ontology import OntologyService
from knowledge.services.session import Session
from knowledge.services.users import UserManagementServiceAPI, User, UserRole


class OntologyFlow(TestCase):
    """
    Testing Ontology flows
    ----------------------
    The tested functionality is:
    - Login to the ontology service
    - Get the ontology context
    - Export the ontology
    - Test the access to:
        - Concepts / Classes
        - Data properties
        - Object properties
    """

    # -----------------------------------------------------------------------------------------------------------------
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(
        service_url=os.environ.get("INSTANCE"), service_endpoint="graph/v1"
    )
    ontology: OntologyService = OntologyService(service_url=os.environ.get("INSTANCE"), service_endpoint="ontology/v1")

    """User management service."""
    tenant_api_key: str = os.environ.get("TENANT_API_KEY")
    LIMIT: int = 10000

    def test_1_ontology(self):
        """
        Test ontology login and context.
        """
        list_user_all: List[User] = self.user_management.listing_users(self.tenant_api_key)
        admin_external_user: Optional[str] = None
        for u_i in list_user_all:
            if UserRole.ADMIN in u_i.user_roles:
                admin_external_user = u_i.external_user_id
        self.assertIsNotNone(admin_external_user)
        self.ontology.login(self.tenant_api_key, admin_external_user)
        context: Optional[OntologyContext] = self.ontology.context()
        self.assertIsNotNone(context)
        self.assertIsNotNone(context.context)
        self.assertIsNotNone(context.tenant_id)
        self.assertIsNotNone(context.iri)
        self.assertIsNotNone(context.labels)
        self.assertGreater(len(context.labels), 1)
        self.assertIsNotNone(context.concepts)
        self.assertGreater(len(context.concepts), 1)
        self.assertIsNotNone(context.properties)
        self.assertGreater(len(context.properties), 1)

    def test_2_ontology_export(self):
        """
        Test ontology export.
        """
        list_user_all: List[User] = self.user_management.listing_users(self.tenant_api_key)
        admin_external_user: Optional[str] = None
        for u_i in list_user_all:
            if UserRole.ADMIN in u_i.user_roles:
                admin_external_user = u_i.external_user_id
        self.assertIsNotNone(admin_external_user)
        session: Session = self.ontology.login(self.tenant_api_key, admin_external_user)
        context: Optional[OntologyContext] = self.ontology.context()
        rdf: str = self.ontology.rdf_export(context.context)
        self.assertIsNotNone(rdf)
        ontology_inst: Ontology = ontology_import(rdf, session.tenant_id, context.context)
        self.assertIsNotNone(ontology_inst)
        for o in ontology_inst.classes:
            if o.iri.startswith("http://"):
                # Skip the standard classes
                continue
            concept: OntologyClass = self.ontology.concept(context.context, o.iri)
            self.assertIsNotNone(concept)
            self.assertIsNotNone(concept.iri)
            self.assertIsNotNone(concept.tenant_id)
            self.assertIsNotNone(concept.labels)
        for dp in ontology_inst.data_properties:
            prop: OntologyProperty = self.ontology.property(context.context, dp.iri)
            self.assertIsNotNone(prop.iri)
            self.assertIsNotNone(prop.tenant_id)
            self.assertIsNotNone(prop.labels)
            self.assertTrue(prop.is_data_property)
        for op in ontology_inst.object_properties:
            prop: OntologyProperty = self.ontology.property(context.context, op.iri)
            self.assertIsNotNone(prop.iri)
            self.assertIsNotNone(prop.tenant_id)
            self.assertIsNotNone(prop.labels)
            self.assertFalse(prop.is_data_property)
