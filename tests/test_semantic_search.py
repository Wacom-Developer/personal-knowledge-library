# -*- coding: utf-8 -*-
# Copyright © 2023-present Wacom. All rights reserved.
import logging
import os
import time
import uuid
from typing import List, Dict, Any
from unittest import TestCase

from faker import Faker

from knowledge.base.language import JA_JP, EN_US, DE_DE, LocaleCode
from knowledge.base.search import VectorDBDocument
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.search import SemanticSearchClient
from knowledge.services.session import PermanentSession

fakers_configured: Dict[str, Faker] = {
    EN_US: Faker('en_US'),
    DE_DE: Faker('de_DE'),
    JA_JP: Faker('ja_JP')
}

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class VectorSearchTest(TestCase):
    """
    VectorSearchTest
    """
    semantic_search_client: SemanticSearchClient = SemanticSearchClient(os.environ.get("INSTANCE"))
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(service_url=os.environ.get("INSTANCE"))
    iterations: int = 20
    label_uri: str = uuid.uuid4().hex
    document_uri: str = uuid.uuid4().hex
    test_uuid: str = uuid.uuid4().hex
    tenant_api_key: str = os.environ.get("TENANT_API_KEY")
    external_user_id: str = os.environ.get("EXTERNAL_USER_ID")

    def setUp(self):
        """
        Set up the test. Login to the knowledge service.
        """
        try:
            self.tenant_id = self.semantic_search_client.current_session.tenant_id
        except WacomServiceException:
            try:
                session: PermanentSession = self.knowledge_client.login(self.tenant_api_key, self.external_user_id)
                self.semantic_search_client.register_token(session.auth_token, session.refresh_token)
                self.tenant_id = self.semantic_search_client.current_session.tenant_id
            except WacomServiceException as e:
                raise Exception(f"Failed to login: {e}") from e

    def test_1_search_label_ja(self):
        """
        Test search label.
        """
        words_ja: int = self.semantic_search_client.count_labels(JA_JP)
        self.assertGreaterEqual(words_ja, 1)
        timings: List[float] = []
        for _ in range(0, self.iterations):
            t0: float = time.perf_counter()
            results = self.semantic_search_client.labels_search(query=fakers_configured[JA_JP].word(), locale=JA_JP)
            self.assertGreater(len(results.results), 0)
            t1: float = time.perf_counter()
            timings.append(t1 - t0)
            for result in results.results:
                labels: List[VectorDBDocument] = self.semantic_search_client.retrieve_labels(JA_JP, result.entity_uri)
                self.assertGreaterEqual(len(labels), 1)
        logger.debug(f"Average fuzzy matching time: {sum(timings) / len(timings)}")
        self.assertLessEqual(sum(timings) / len(timings), 0.5,
                             "Average fuzzy matching time should be less than 0.5 s")

    def test_2_search_label_en(self):
        """
        Test search label.
        """
        words_en: int = self.semantic_search_client.count_labels(EN_US)
        self.assertGreaterEqual(words_en, 1)
        timings: List[float] = []
        for _ in range(0, self.iterations):
            t0: float = time.perf_counter()
            results = self.semantic_search_client.labels_search(query=fakers_configured[EN_US].word(), locale=EN_US)
            self.assertGreater(len(results.results), 0)
            t1: float = time.perf_counter()
            timings.append(t1 - t0)
            for result in results.results:
                labels: List[VectorDBDocument] = self.semantic_search_client.retrieve_labels(EN_US, result.entity_uri)
                self.assertGreaterEqual(len(labels), 1)
        self.assertLessEqual(sum(timings) / len(timings), 0.5,
                             "Average fuzzy matching time should be less than 0.5 s")

    def test_3_search_label_de(self):
        """
        Test search label.
        """
        words_de: int = self.semantic_search_client.count_labels(DE_DE)
        self.assertGreaterEqual(words_de, 1)
        timings: List[float] = []
        for _ in range(0, self.iterations):
            t0: float = time.perf_counter()
            results = self.semantic_search_client.labels_search(query=fakers_configured[DE_DE].word(), locale=DE_DE)
            self.assertGreater(len(results.results), 0)
            t1: float = time.perf_counter()
            timings.append(t1 - t0)
            for result in results.results:
                labels: List[VectorDBDocument] = self.semantic_search_client.retrieve_labels(DE_DE, result.entity_uri)
                self.assertGreaterEqual(len(labels), 1)
        self.assertLessEqual(sum(timings) / len(timings), 0.5,
                             "Average fuzzy matching time should be less than 0.5 s")

    def test_5_search_document_en(self):
        """
        Test search document.
        """
        docs_de: int = self.semantic_search_client.count_documents(DE_DE)
        self.assertGreaterEqual(docs_de, 1)
        timings: List[float] = []
        for _ in range(0, self.iterations):
            t0: float = time.perf_counter()
            results = self.semantic_search_client.document_search(query=fakers_configured[DE_DE].word(), locale=DE_DE)
            self.assertGreater(len(results.results), 0)
            t1: float = time.perf_counter()
            timings.append(t1 - t0)
            for result in results.results:
                uri: str = result.content_uri
                documents: List[VectorDBDocument] = self.semantic_search_client.retrieve_documents_chunks(DE_DE, uri)
                self.assertGreaterEqual(len(documents), 1)
        self.assertLessEqual(sum(timings) / len(timings), 1,
                             "Average document search time should be less than 1 s")

    def test_6_search_document_de(self):
        """
        Test search document.
        """
        docs_en: int = self.semantic_search_client.count_documents(EN_US)
        self.assertGreaterEqual(docs_en, 1)
        timings: List[float] = []
        for _ in range(0, self.iterations):
            t0: float = time.perf_counter()
            results = self.semantic_search_client.document_search(query=fakers_configured[EN_US].word(), locale=EN_US)
            self.assertGreater(len(results.results), 0)
            t1: float = time.perf_counter()
            timings.append(t1 - t0)
            for result in results.results:
                uri: str = result.content_uri
                documents: List[VectorDBDocument] = self.semantic_search_client.retrieve_documents_chunks(EN_US, uri)
                self.assertGreaterEqual(len(documents), 1)
        self.assertLessEqual(sum(timings) / len(timings), 1,
                             "Average document search time should be less than 1 s")

    def test_7_search_document_ja(self):
        """
        Test search document.
        """
        docs_en: int = self.semantic_search_client.count_documents(JA_JP)
        self.assertGreaterEqual(docs_en, 1)
        timings: List[float] = []
        for _ in range(0, self.iterations):
            t0: float = time.perf_counter()
            results = self.semantic_search_client.document_search(query=fakers_configured[JA_JP].word(), locale=JA_JP)
            self.assertGreater(len(results.results), 0)
            t1: float = time.perf_counter()
            timings.append(t1 - t0)
            for result in results.results:
                uri: str = result.content_uri
                documents: List[VectorDBDocument] = self.semantic_search_client.retrieve_documents_chunks(JA_JP, uri)
                self.assertGreaterEqual(len(documents), 1)
        self.assertLessEqual(sum(timings) / len(timings), 1,
                         "Average document search time should be less than 1 s")
