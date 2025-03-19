# -*- coding: utf-8 -*-
# Copyright © 2023-24 Wacom. All rights reserved.
import logging
import os
import uuid
from typing import List, Optional
from unittest import TestCase

import pytest
from faker import Faker
from ontospy import Ontospy

from knowledge.base.language import JA_JP, EN_US, DE_DE, LocaleCode
from knowledge.base.ontology import OntologyClassReference
from knowledge.nel.base import KnowledgeGraphEntity
from knowledge.nel.engine import WacomEntityLinkingEngine
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.users import UserManagementServiceAPI, User, UserRole

THING_OBJECT: OntologyClassReference = OntologyClassReference("wacom", "core", "Thing")


@pytest.fixture(scope="class")
def cache_class(request):
    class ClassDB:
        """
        Class to store data for the test cases.
        """

        def __init__(self):
            self.__external_id: Optional[str] = None
            self.__token: Optional[str] = None
            self.__model: Optional[Ontospy] = None

        @property
        def external_id(self) -> Optional[str]:
            """External user id."""
            return self.__external_id

        @external_id.setter
        def external_id(self, external_id: Optional[str]):
            self.__external_id = external_id

        @property
        def token(self) -> Optional[str]:
            """User token."""
            return self.__token

        @token.setter
        def token(self, token: Optional[str]):
            self.__token = token

        @property
        def model(self) -> Optional[Ontospy]:
            """Ontology model."""
            return self.__model

        @model.setter
        def model(self, model: Optional[Ontospy]):
            self.__model = model

    # set a class attribute on the invoking test context
    request.cls.cache = ClassDB()


@pytest.mark.usefixtures("cache_class")
class EntityFlow(TestCase):
    """
    Testing the entity flow
    ---------------------
    - Create entity

    """

    # -----------------------------------------------------------------------------------------------------------------
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Wacom Knowledge Listing", service_url=os.environ.get("INSTANCE")
    )
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=os.environ.get("INSTANCE"))
    ontology: OntologyService = OntologyService(service_url=os.environ.get("INSTANCE"))
    #  Wacom Named Entities Linking
    nel_client: WacomEntityLinkingEngine = WacomEntityLinkingEngine(
        service_url=os.environ.get("INSTANCE"), service_endpoint=WacomEntityLinkingEngine.SERVICE_ENDPOINT
    )

    """User management service."""
    tenant_api_key: str = os.environ.get("TENANT_API_KEY")
    LIMIT: int = 10000

    def test_1_create_user(self):
        """Create a user."""
        # Create an external user id
        self.cache.external_id = str(uuid.uuid4())
        # Create user
        _, token, refresh, expire = self.user_management.create_user(
            self.tenant_api_key,
            external_id=self.cache.external_id,
            meta_data={"account-type": "qa-test"},
            roles=[UserRole.USER],
        )
        self.cache.token = token

    def test_2_nel_en(self):
        """Test the named entity linking for English."""
        en_us: LocaleCode = EN_US
        entities, _, _ = self.knowledge_client.listing(
            THING_OBJECT, page_id=None, limit=10, locale=en_us, auth_key=self.cache.token
        )
        fake: Faker = Faker(en_us)
        for ent in entities:
            if ent.use_for_nel and ent.label_lang(en_us) is not None:
                text: str = f"{fake.text()} Do not forget about {ent.label_lang(en_us).content}."
                self.assertTrue(self.nel_client.is_language_supported(en_us))
                linked_entities: List[KnowledgeGraphEntity] = self.nel_client.link_personal_entities(
                    text, language_code=en_us, auth_key=self.cache.token
                )
                self.assertGreaterEqual(len(linked_entities), 1)

    def test_3_nel_ja(self):
        """Test the named entity linking for Japanese."""
        ja_jp: LocaleCode = JA_JP
        entities, _, _ = self.knowledge_client.listing(
            THING_OBJECT, page_id=None, limit=10, locale=ja_jp, auth_key=self.cache.token
        )
        fake: Faker = Faker(ja_jp)
        for ent in entities:
            if ent.use_for_nel and ent.label_lang(ja_jp) is not None:
                text: str = f"{fake.text()}{ent.label_lang(ja_jp).content}"
                self.assertTrue(self.nel_client.is_language_supported(ja_jp))
                linked_entities: List[KnowledgeGraphEntity] = self.nel_client.link_personal_entities(
                    text=text, language_code=ja_jp, auth_key=self.cache.token
                )
                self.assertGreaterEqual(len(linked_entities), 1)

    def test_4_nel_de(self):
        """Test the named entity linking for German."""
        de_de: LocaleCode = DE_DE
        entities, _, _ = self.knowledge_client.listing(
            THING_OBJECT, page_id=None, limit=10, locale=de_de, auth_key=self.cache.token
        )
        fake: Faker = Faker(de_de)
        for ent in entities:
            if ent.use_for_nel and ent.label_lang(de_de) is not None:
                text: str = f"{fake.text()}. {ent.label_lang(de_de).content}."
                self.assertTrue(self.nel_client.is_language_supported(de_de))
                linked_entities: List[KnowledgeGraphEntity] = self.nel_client.link_personal_entities(
                    text, language_code=de_de, auth_key=self.cache.token
                )
                self.assertGreaterEqual(len(linked_entities), 1)

    def teardown_class(self):
        """Clean up the test environment."""
        list_user_all: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=EntityFlow.LIMIT)
        for u_i in list_user_all:
            if "account-type" in u_i.meta_data and u_i.meta_data.get("account-type") == "qa-test":
                logging.info(f"Clean user {u_i.external_user_id}")
                try:
                    self.user_management.delete_user(
                        self.tenant_api_key, external_id=u_i.external_user_id, internal_id=u_i.id, force=True
                    )
                except WacomServiceException as we:
                    logging.error(f"Error during user deletion: {we}")
