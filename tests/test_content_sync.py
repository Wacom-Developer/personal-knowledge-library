# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""
Integration tests for ContentClient (synchronous client).

Flow for each scenario:
    1. Create test user
    2. Create a wacom:core#Page entity
    3. Upload content file linked to the entity URI
    4. Update tags via PATCH
    5. Update metadata via PATCH
    6. Verify with GET (info endpoint)
    7. Replace file via PUT
    8. Verify updated content
    9. Delete the single content item
   10. Multi-file: upload two files to the same entity, verify listing, delete all
   11. Delete entity and clean up test user

Requires environment variables:
    - INSTANCE: URL of the service instance
    - TENANT_API_KEY: Tenant API key for authentication
"""
import logging
import os
import uuid
from pathlib import Path
from typing import List, Optional
from unittest import TestCase

import pytest

from knowledge.base.content import ContentObject
from knowledge.base.language import EN_US
from knowledge.base.ontology import (
    ThingObject,
    OntologyClassReference,
    OntologyPropertyReference,
    DataProperty,
)
from knowledge.services.content import ContentClient
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.users import UserManagementServiceAPI, User, UserRole

# -----------------------------------------------------------------------------------------------------------------
ASSETS_DIR: Path = Path(__file__).parent.parent / "assets"
DUMMY_PNG: Path = ASSETS_DIR / "dummy.png"
WIKIDATA_PNG: Path = ASSETS_DIR / "wikidata.png"
UIM_PNG: Path = ASSETS_DIR / "uim.png"
LIMIT: int = 10000
PAGE_TYPE: OntologyClassReference = OntologyClassReference.parse("wacom:core#Page")


def create_page_entity() -> ThingObject:
    """Create a minimal wacom:core#Page entity for testing."""
    page: ThingObject = ThingObject(concept_type=PAGE_TYPE)
    page.add_label("Test Content Page", EN_US)
    page.add_description("Page entity created by content integration tests.", EN_US)
    page.add_data_property(
        DataProperty(
            content="Integration test page content.",
            property_ref=OntologyPropertyReference.parse("wacom:core#content"),
            language_code=EN_US,
        )
    )
    page.use_full_text_index = False
    page.use_vector_index = False
    page.use_vector_index_document = False
    page.use_for_nel = False
    return page


# -----------------------------------------------------------------------------------------------------------------
# Shared state cache fixture
# -----------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope="class")
def cache_class(request):
    """Cache shared state across tests in a class."""

    class Cache:
        def __init__(self):
            self.external_id: Optional[str] = None
            self.entity_uri: Optional[str] = None
            self.content_id: Optional[str] = None
            self.multi_content_ids: List[str] = []

    request.cls.cache = Cache()


# -----------------------------------------------------------------------------------------------------------------
# Test class
# -----------------------------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("cache_class")
class TestContentClientSync(TestCase):
    """
    Integration tests for the synchronous ContentClient.

    Tests the full content lifecycle: upload → tag/metadata update →
    verify → file update → verify → delete. Also tests multi-file uploads
    for a single entity.
    """

    instance: str = os.environ.get("INSTANCE")
    tenant_api_key: str = os.environ.get("TENANT_API_KEY")

    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Content Test (sync)",
        service_url=os.environ.get("INSTANCE"),
        service_endpoint="graph/v1",
    )
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(
        service_url=os.environ.get("INSTANCE"),
        service_endpoint="graph/v1",
    )
    content_client: ContentClient = ContentClient(
        service_url=os.environ.get("INSTANCE"),
        application_name="Content Test (sync)",
    )

    # =================================================================================================================
    # Setup
    # =================================================================================================================

    def test_01_create_user(self):
        """Create an isolated test user."""
        if not self.instance or not self.tenant_api_key:
            pytest.skip("INSTANCE or TENANT_API_KEY not set")
        self.cache.external_id = str(uuid.uuid4())
        _, token, refresh, _ = self.user_management.create_user(
            self.tenant_api_key,
            external_id=self.cache.external_id,
            meta_data={"account-type": "qa-test-content-sync"},
            roles=[UserRole.USER],
        )
        self.assertIsNotNone(token)
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        self.content_client.login(self.tenant_api_key, self.cache.external_id)

    def test_02_create_page_entity(self):
        """Create a wacom:core#Page entity to attach content to."""
        if not self.cache.external_id:
            pytest.skip("No test user available")
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        page: ThingObject = create_page_entity()
        self.cache.entity_uri = self.knowledge_client.create_entity(page)
        self.assertIsNotNone(self.cache.entity_uri)
        logging.info(f"Created entity: {self.cache.entity_uri}")

    # =================================================================================================================
    # Single-file content lifecycle
    # =================================================================================================================

    def test_03_upload_content(self):
        """Upload a file and link it to the entity URI."""
        if not self.cache.entity_uri:
            pytest.skip("No entity available")
        if not DUMMY_PNG.exists():
            pytest.skip(f"Test asset not found: {DUMMY_PNG}")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        file_bytes: bytes = DUMMY_PNG.read_bytes()
        content_id: str = self.content_client.upload_content(
            uri=self.cache.entity_uri,
            file_content=file_bytes,
            filename=DUMMY_PNG.name,
            mimetype="image/png",
        )
        self.assertIsNotNone(content_id)
        self.assertGreater(len(content_id), 0)
        self.cache.content_id = content_id
        logging.info(f"Uploaded content: {content_id}")

    def test_04_update_tags(self):
        """Patch the content item to add tags."""
        if not self.cache.content_id:
            pytest.skip("No content item available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        self.content_client.update_content_tags(
            content_id=self.cache.content_id,
            tags=["test-tag", "integration", "sync"],
        )

    def test_05_update_metadata(self):
        """Patch the content item to add metadata."""
        if not self.cache.content_id:
            pytest.skip("No content item available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        self.content_client.update_content_metadata(
            content_id=self.cache.content_id,
            metadata={"source": "integration-test", "client": "sync"},
        )

    def test_06_verify_content_info(self):
        """Retrieve content info and assert tags and metadata are present."""
        if not self.cache.content_id:
            pytest.skip("No content item available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        info: ContentObject = self.content_client.get_content_info(self.cache.content_id)
        self.assertEqual(info.id, self.cache.content_id)
        self.assertIn("test-tag", info.tags)
        self.assertIn("integration", info.tags)
        self.assertIn("sync", info.tags)
        self.assertEqual(info.metadata.get("source"), "integration-test")
        self.assertEqual(info.metadata.get("client"), "sync")
        self.assertIsNotNone(info.mime_type)
        self.assertIsNotNone(info.date_added)
        self.assertIsNotNone(info.date_modified)
        logging.info(f"Content info verified: mime_type={info.mime_type}, tags={info.tags}")

    def test_07_verify_list_content(self):
        """List all content for the entity and confirm the item is present."""
        if not self.cache.entity_uri or not self.cache.content_id:
            pytest.skip("No entity or content item available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        items: List[ContentObject] = self.content_client.list_content(self.cache.entity_uri)
        self.assertGreaterEqual(len(items), 1)
        ids = [item.id for item in items]
        self.assertIn(self.cache.content_id, ids)

    def test_08_update_content_file(self):
        """Replace the stored file with updated content."""
        if not self.cache.content_id:
            pytest.skip("No content item available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        updated_bytes: bytes = UIM_PNG.read_bytes()
        self.content_client.update_content_file(
            content_id=self.cache.content_id,
            file_content=updated_bytes,
            filename="updated.bin",
        )

    def test_09_verify_updated_file(self):
        """Download the content and confirm it matches the updated bytes."""
        if not self.cache.content_id:
            pytest.skip("No content item available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        items: List[ContentObject] = self.content_client.list_content(self.cache.entity_uri)
        for item in items:
            downloaded: bytes = self.content_client.download_content(item.id)
            reference_bytes: bytes = UIM_PNG.read_bytes()
            self.assertEqual(downloaded, reference_bytes)

    def test_10_update_content_combined(self):
        """Use update_content to patch both metadata and tags in one call."""
        if not self.cache.content_id:
            pytest.skip("No content item available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        result: ContentObject = self.content_client.update_content(
            content_id=self.cache.content_id,
            metadata={"source": "integration-test", "client": "sync", "updated": "true"},
            tags=["test-tag", "integration", "sync", "updated"],
        )
        self.assertIn("updated", result.tags)
        self.assertEqual(result.metadata.get("updated"), "true")

    def test_11_delete_single_content(self):
        """Delete the single content item and verify it is gone."""
        if not self.cache.content_id:
            pytest.skip("No content item available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        self.content_client.delete_content(self.cache.content_id)
        items: List[ContentObject] = self.content_client.list_content(self.cache.entity_uri)
        for item in items:
            if item.id == self.cache.content_id and not item.is_deleted:
                self.fail("Deleted content item still present in list_content results")

    # =================================================================================================================
    # Multi-file content lifecycle
    # =================================================================================================================

    def test_12_upload_multiple_files(self):
        """Upload two content files to the same entity."""
        if not self.cache.entity_uri:
            pytest.skip("No entity available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        file_a: bytes = UIM_PNG.read_bytes()
        file_b: bytes = WIKIDATA_PNG.read_bytes()
        id_a: str = self.content_client.upload_content(
            uri=self.cache.entity_uri,
            file_content=file_a,
            filename="uim.png",
            mimetype="image/png",
        )
        id_b: str = self.content_client.upload_content(
            uri=self.cache.entity_uri,
            file_content=file_b,
            filename="wikidata.png",
            mimetype="image/png",
        )
        self.assertIsNotNone(id_a)
        self.assertIsNotNone(id_b)
        self.assertNotEqual(id_a, id_b)
        self.cache.multi_content_ids = [id_a, id_b]
        logging.info(f"Uploaded two content items: {id_a}, {id_b}")

    def test_13_verify_multiple_files_listed(self):
        """Verify that list_content returns both uploaded files."""
        if not self.cache.multi_content_ids:
            pytest.skip("No multi-file content available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        items: List[ContentObject] = self.content_client.list_content(self.cache.entity_uri)
        ids = [item.id for item in items]
        for content_id in self.cache.multi_content_ids:
            self.assertIn(content_id, ids)
        self.assertGreaterEqual(len(items), 2)

    def test_14_verify_each_file_downloadable(self):
        """Download each uploaded file and verify the expected bytes."""
        if not self.cache.multi_content_ids:
            pytest.skip("No multi-file content available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        expected = {
            self.cache.multi_content_ids[0]: UIM_PNG.read_bytes(),
            self.cache.multi_content_ids[1]: WIKIDATA_PNG.read_bytes(),
        }
        for content_id, expected_bytes in expected.items():
            downloaded: bytes = self.content_client.download_content(content_id)
            self.assertEqual(downloaded, expected_bytes)

    def test_15_delete_all_content(self):
        """Delete all content for the entity and verify the list is empty."""
        if not self.cache.entity_uri:
            pytest.skip("No entity available")
        self.content_client.login(self.tenant_api_key, self.cache.external_id)
        self.content_client.delete_all_content(self.cache.entity_uri)
        items: List[ContentObject] = self.content_client.list_content(self.cache.entity_uri)
        self.assertEqual(len(items), 0)
        self.cache.multi_content_ids = []

    # =================================================================================================================
    # Teardown
    # =================================================================================================================

    def test_16_delete_entity(self):
        """Delete the test entity."""
        if not self.cache.entity_uri:
            pytest.skip("No entity available")
        self.knowledge_client.login(self.tenant_api_key, self.cache.external_id)
        self.knowledge_client.delete_entity(self.cache.entity_uri, force=True)
        self.cache.entity_uri = None

    def teardown_class(self):
        """Remove all test users created during the test run."""
        all_users: List[User] = self.user_management.listing_users(self.tenant_api_key, limit=LIMIT)
        for user in all_users:
            if user.meta_data.get("account-type") == "qa-test-content-sync":
                logging.info(f"Cleaning up test user: {user.external_user_id}")
                self.user_management.delete_user(
                    self.tenant_api_key,
                    external_id=user.external_user_id,
                    internal_id=user.id,
                    force=True,
                )
