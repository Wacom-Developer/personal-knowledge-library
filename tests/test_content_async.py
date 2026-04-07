# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""
Integration tests for AsyncContentClient.

Flow:
    1. Create test user
    2. Create a wacom:core#Page entity
    3. Upload content file linked to the entity URI
    4. Update tags via PATCH
    5. Update metadata via PATCH
    6. Verify with GET (info endpoint)
    7. List content and confirm item is present
    8. Replace file via PUT
    9. Verify downloaded file matches updated bytes
   10. Update metadata and tags in one call (update_content)
   11. Delete the single content item and verify it is gone
   12. Multi-file: upload two files to the same entity
   13. Verify list_content returns both files
   14. Verify each file is downloadable with correct bytes
   15. Delete all content for the entity
   16. Delete entity and clean up test user

Requires environment variables:
    - INSTANCE: URL of the service instance
    - TENANT_API_KEY: Tenant API key for authentication
"""
import logging
import os
import uuid
from pathlib import Path
from typing import List, Optional

import loguru
import pytest
import pytest_asyncio

from knowledge.base.content import ContentObject
from knowledge.base.language import EN_US
from knowledge.base.ontology import (
    ThingObject,
    OntologyClassReference,
    OntologyPropertyReference,
    DataProperty,
)
from knowledge.services.asyncio.content import AsyncContentClient
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.asyncio.users import AsyncUserManagementService
from knowledge.services.base import WacomServiceException
from knowledge.services.users import UserRole, User

# -----------------------------------------------------------------------------------------------------------------
ASSETS_DIR: Path = Path(__file__).parent.parent / "assets"
DUMMY_PNG: Path = ASSETS_DIR / "dummy.png"
PAGE_TYPE: OntologyClassReference = OntologyClassReference.parse("wacom:core#Page")
LIMIT: int = 10000
logger = loguru.logger

# -----------------------------------------------------------------------------------------------------------------
# Module-level state shared across ordered test functions
# -----------------------------------------------------------------------------------------------------------------
_tenant_api_key: str = os.environ.get("TENANT_API_KEY", "")
_instance: str = os.environ.get("INSTANCE", "")

_external_id: Optional[str] = None
_entity_uri: Optional[str] = None
_content_id: Optional[str] = None
_multi_content_ids: List[str] = []

# -----------------------------------------------------------------------------------------------------------------
# Module-level clients
# -----------------------------------------------------------------------------------------------------------------
knowledge_client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(
    service_url=_instance,
    application_name="Content Test (async)",
)
user_management: AsyncUserManagementService = AsyncUserManagementService(
    service_url=_instance,
    application_name="Content Test (async)",
)
content_client: AsyncContentClient = AsyncContentClient(
    service_url=_instance,
    application_name="Content Test (async)",
)


def _require_env() -> None:
    """Skip the test if required environment variables are not set."""
    if not _instance or not _tenant_api_key:
        pytest.skip("INSTANCE or TENANT_API_KEY not set")


def create_page_entity() -> ThingObject:
    """Create a minimal wacom:core#Page entity for testing."""
    page: ThingObject = ThingObject(concept_type=PAGE_TYPE)
    page.add_label("Async Test Content Page", EN_US)
    page.add_description("Page entity created by async content integration tests.", EN_US)
    page.add_data_property(
        DataProperty(
            content="Async integration test page content.",
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
# Session-scoped fixture to close all async HTTP clients after the test module
# -----------------------------------------------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="module", autouse=True, loop_scope="module")
async def close_async_clients():
    """Close all module-level async HTTP clients after tests finish."""
    yield
    await knowledge_client.close()
    await user_management.close()
    await content_client.close()


# =================================================================================================================
# Setup
# =================================================================================================================


async def test_01_create_user():
    """Create an isolated test user and log in all clients."""
    global _external_id
    _require_env()
    _external_id = str(uuid.uuid4())
    _, token, refresh, _ = await user_management.create_user(
        _tenant_api_key,
        external_id=_external_id,
        meta_data={"account-type": "qa-test-content-async"},
        roles=[UserRole.USER],
    )
    assert token is not None
    await knowledge_client.login(_tenant_api_key, _external_id)
    await content_client.login(_tenant_api_key, _external_id)
    logger.info(f"Created test user: {_external_id}")


async def test_02_create_page_entity():
    """Create a wacom:core#Page entity to attach content to."""
    global _entity_uri
    if not _external_id:
        pytest.skip("No test user available")
    await knowledge_client.login(_tenant_api_key, _external_id)
    await content_client.login(_tenant_api_key, _external_id)
    page: ThingObject = create_page_entity()
    _entity_uri = await knowledge_client.create_entity(page)
    assert _entity_uri is not None
    logger.info(f"Created entity: {_entity_uri}")


# =================================================================================================================
# Single-file content lifecycle
# =================================================================================================================


async def test_03_upload_content():
    """Upload a file and link it to the entity URI."""
    global _content_id
    if not _entity_uri:
        pytest.skip("No entity available")
    if not DUMMY_PNG.exists():
        pytest.skip(f"Test asset not found: {DUMMY_PNG}")
    await content_client.login(_tenant_api_key, _external_id)
    file_bytes: bytes = DUMMY_PNG.read_bytes()
    _content_id = await content_client.upload_content(
        uri=_entity_uri,
        file_content=file_bytes,
        filename=DUMMY_PNG.name,
    )
    assert _content_id is not None
    assert len(_content_id) > 0
    logger.info(f"Uploaded content: {_content_id}")


async def test_04_update_tags():
    """Patch the content item to add tags."""
    if not _content_id:
        pytest.skip("No content item available")
    await content_client.login(_tenant_api_key, _external_id)
    await content_client.update_content_tags(
        content_id=_content_id,
        tags=["test-tag", "integration", "async"],
    )


async def test_05_update_metadata():
    """Patch the content item to add metadata."""
    if not _content_id:
        pytest.skip("No content item available")
    await content_client.login(_tenant_api_key, _external_id)
    await content_client.update_content_metadata(
        content_id=_content_id,
        metadata={"source": "integration-test", "client": "async"},
    )


async def test_06_verify_content_info():
    """Retrieve content info and assert tags and metadata are present."""
    if not _content_id:
        pytest.skip("No content item available")
    await content_client.login(_tenant_api_key, _external_id)
    info: ContentObject = await content_client.get_content_info(_content_id)
    assert info.id == _content_id
    assert "test-tag" in info.tags
    assert "integration" in info.tags
    assert "async" in info.tags
    assert info.metadata.get("source") == "integration-test"
    assert info.metadata.get("client") == "async"
    assert info.mime_type is not None
    assert info.date_added is not None
    assert info.date_modified is not None
    logger.info(f"Content info verified: mime_type={info.mime_type}, tags={info.tags}")


async def test_07_verify_list_content():
    """List all content for the entity and confirm the item is present."""
    if not _entity_uri or not _content_id:
        pytest.skip("No entity or content item available")
    await content_client.login(_tenant_api_key, _external_id)
    items: List[ContentObject] = await content_client.list_content(_entity_uri)
    assert len(items) >= 1
    ids = [item.id for item in items]
    assert _content_id in ids


async def test_08_update_content_file():
    """Replace the stored file with updated content."""
    if not _content_id:
        pytest.skip("No content item available")
    await content_client.login(_tenant_api_key, _external_id)
    updated_bytes: bytes = b"async-updated-content-bytes-for-testing"
    await content_client.update_content_file(
        content_id=_content_id,
        file_content=updated_bytes,
        filename="updated.bin",
    )


async def test_09_verify_updated_file():
    """Download the content and confirm it matches the updated bytes."""
    if not _content_id:
        pytest.skip("No content item available")
    await content_client.login(_tenant_api_key, _external_id)
    downloaded: bytes = await content_client.download_content(_content_id)
    assert downloaded == b"async-updated-content-bytes-for-testing"


async def test_10_update_content_combined():
    """Use update_content to patch both metadata and tags in one call."""
    if not _content_id:
        pytest.skip("No content item available")
    await content_client.login(_tenant_api_key, _external_id)
    result: ContentObject = await content_client.update_content(
        content_id=_content_id,
        metadata={"source": "integration-test", "client": "async", "updated": "true"},
        tags=["test-tag", "integration", "async", "updated"],
    )
    assert "updated" in result.tags
    assert result.metadata.get("updated") == "true"


async def test_11_delete_single_content():
    """Delete the single content item and verify it is gone."""
    global _content_id
    if not _content_id:
        pytest.skip("No content item available")
    await content_client.login(_tenant_api_key, _external_id)
    await content_client.delete_content(_content_id)
    items: List[ContentObject] = await content_client.list_content(_entity_uri)
    for item in items:
        if item.id == _content_id and not item.is_deleted:
            assert item.is_deleted


# =================================================================================================================
# Multi-file content lifecycle
# =================================================================================================================


async def test_12_upload_multiple_files():
    """Upload two content files to the same entity."""
    global _multi_content_ids
    if not _entity_uri:
        pytest.skip("No entity available")
    await content_client.login(_tenant_api_key, _external_id)
    file_a: bytes = b"async-content-file-alpha"
    file_b: bytes = b"async-content-file-beta"
    id_a: str = await content_client.upload_content(
        uri=_entity_uri,
        file_content=file_a,
        filename="alpha.bin",
    )
    id_b: str = await content_client.upload_content(
        uri=_entity_uri,
        file_content=file_b,
        filename="beta.bin",
    )
    assert id_a is not None
    assert id_b is not None
    assert id_a != id_b
    _multi_content_ids = [id_a, id_b]
    logger.info(f"Uploaded two content items: {id_a}, {id_b}")


async def test_13_verify_multiple_files_listed():
    """Verify that list_content returns both uploaded files."""
    if not _multi_content_ids:
        pytest.skip("No multi-file content available")
    await content_client.login(_tenant_api_key, _external_id)
    items: List[ContentObject] = await content_client.list_content(_entity_uri)
    ids = [item.id for item in items]
    for content_id in _multi_content_ids:
        assert content_id in ids
    assert len(items) >= 2


async def test_14_verify_each_file_downloadable():
    """Download each uploaded file and verify the expected bytes."""
    if not _multi_content_ids:
        pytest.skip("No multi-file content available")
    await content_client.login(_tenant_api_key, _external_id)
    expected = {
        _multi_content_ids[0]: b"async-content-file-alpha",
        _multi_content_ids[1]: b"async-content-file-beta",
    }
    for content_id, expected_bytes in expected.items():
        downloaded: bytes = await content_client.download_content(content_id)
        assert downloaded == expected_bytes


async def test_15_delete_all_content():
    """Delete all content for the entity and verify the list is empty."""
    global _multi_content_ids
    if not _entity_uri:
        pytest.skip("No entity available")
    await content_client.login(_tenant_api_key, _external_id)
    await content_client.delete_all_content(_entity_uri)
    items: List[ContentObject] = await content_client.list_content(_entity_uri)
    assert len(items) == 0
    _multi_content_ids = []


# =================================================================================================================
# Teardown
# =================================================================================================================


async def test_16_delete_entity():
    """Delete the test entity."""
    global _entity_uri
    if not _entity_uri:
        pytest.skip("No entity available")
    await knowledge_client.login(_tenant_api_key, _external_id)
    await knowledge_client.delete_entity(_entity_uri, force=True)
    _entity_uri = None


async def test_17_cleanup_users():
    """Remove all test users created during this module."""
    _require_env()
    try:
        all_users: List[User] = await user_management.listing_users(_tenant_api_key, limit=LIMIT)
        for user in all_users:
            if user.meta_data.get("account-type") == "qa-test-content-async":
                logger.info(f"Deleting test user: {user.external_user_id}")
                try:
                    await user_management.delete_user(
                        _tenant_api_key,
                        external_id=user.external_user_id,
                        internal_id=user.id,
                        force=True,
                    )
                except WacomServiceException as exc:
                    logger.error(f"Error deleting user {user.external_user_id}: {exc}")
    except Exception as exc:
        logger.error(f"Error during user cleanup: {exc}")
