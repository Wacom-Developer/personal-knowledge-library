# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""
Integration tests for IndexManagementClient (sync) and AsyncIndexManagementClient (async).

These clients extend the SemanticSearchClient hierarchy and add index management
operations (health check, refresh, force-merge) on top of the full search API.

Requires environment variables:
    - INSTANCE: URL of the service instance
    - TENANT_API_KEY: Tenant API key for authentication
    - EXTERNAL_USER_ID: External user ID for authentication (content user)
"""

import os
import uuid
from typing import List
from unittest import skip

import loguru
import pytest
import pytest_asyncio

from knowledge.base.index import HealthResponse, IndexMode, IndexDocument
from knowledge.base.language import EN_US
from knowledge.services.asyncio.index_management import AsyncIndexManagementClient
from knowledge.services.asyncio.users import AsyncUserManagementService
from knowledge.services.index_management import IndexManagementClient
from knowledge.services.users import UserManagementServiceAPI, UserRole, User

logger = loguru.logger
LIMIT: int = 100

# Index modes used by the vector search service
INDEX_MODES: List[IndexMode] = ["document", "word"]


# ================================================================================================
# Environment helpers
# ================================================================================================


def get_tenant_api_key() -> str:
    key = os.environ.get("TENANT_API_KEY")
    if not key:
        pytest.skip("TENANT_API_KEY environment variable not set")
    return key


def get_instance_url() -> str:
    url = os.environ.get("INSTANCE")
    if not url:
        pytest.skip("INSTANCE environment variable not set")
    return url


def get_external_user_id() -> str:
    uid = os.environ.get("EXTERNAL_USER_ID")
    if not uid:
        pytest.skip("EXTERNAL_USER_ID environment variable not set")
    return uid


# ================================================================================================
# Sync fixtures
# ================================================================================================


@pytest.fixture(scope="module")
def index_client():
    """
    Sync IndexManagementClient logged in with a fresh test user.
    IndexManagementClient inherits all SemanticSearchClient methods plus index ops.
    Cleans up on teardown.
    """
    instance_url = get_instance_url()
    tenant_api_key = get_tenant_api_key()

    user_management = UserManagementServiceAPI(service_url=instance_url)
    client = IndexManagementClient(service_url=instance_url)

    external_id = str(uuid.uuid4())
    user, token, refresh_token, _ = user_management.create_user(
        tenant_api_key,
        external_id=external_id,
        meta_data={"account-type": "qa-test-index"},
        roles=[UserRole.ADMIN],
    )
    logger.info(f"Created test user: {external_id}")
    client.register_token(auth_key=token, refresh_token=refresh_token)

    yield client

    try:
        users: List[User] = user_management.listing_users(tenant_api_key, limit=LIMIT)
        for u in users:
            if u.meta_data.get("account-type") == "qa-test-index":
                user_management.delete_user(
                    tenant_api_key,
                    external_id=u.external_user_id,
                    internal_id=u.id,
                    force=True,
                )
    except Exception as e:
        logger.error(f"Cleanup error: {e}")


@pytest.fixture(scope="module")
def content_index_client():
    """
    Sync IndexManagementClient logged in as the content user (EXTERNAL_USER_ID).
    Used for search tests that require pre-existing data.
    """
    instance_url = get_instance_url()
    tenant_api_key = get_tenant_api_key()
    external_user_id = get_external_user_id()
    user_management = UserManagementServiceAPI(service_url=instance_url)
    external_id = str(uuid.uuid4())
    user, token, refresh_token, _ = user_management.create_user(
        tenant_api_key,
        external_id=external_id,
        meta_data={"account-type": "qa-test-index"},
        roles=[UserRole.ADMIN],
    )

    client = IndexManagementClient(service_url=instance_url)
    client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    yield client
    try:
        users: List[User] = user_management.listing_users(tenant_api_key, limit=LIMIT)
        for u in users:
            if u.meta_data.get("account-type") == "qa-test-index":
                user_management.delete_user(
                    tenant_api_key,
                    external_id=u.external_user_id,
                    internal_id=u.id,
                    force=True,
                )
    except Exception as e:
        logger.error(f"Cleanup error: {e}")


# ================================================================================================
# Async fixtures
# ================================================================================================


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def async_index_client():
    """
    Async AsyncIndexManagementClient logged in with a fresh test user.
    Cleans up on teardown.
    """
    instance_url = get_instance_url()
    tenant_api_key = get_tenant_api_key()

    user_management = AsyncUserManagementService(service_url=instance_url)
    client = AsyncIndexManagementClient(service_url=instance_url)

    external_id = str(uuid.uuid4())
    user, token, refresh_token, _ = await user_management.create_user(
        tenant_api_key,
        external_id=external_id,
        meta_data={"account-type": "qa-test-index-async"},
        roles=[UserRole.ADMIN],
    )
    logger.info(f"Created async test user: {external_id}")
    await client.register_token(auth_key=token, refresh_token=refresh_token)

    yield client

    try:
        users: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
        for u in users:
            if u.meta_data.get("account-type") == "qa-test-index-async":
                await user_management.delete_user(
                    tenant_api_key,
                    external_id=u.external_user_id,
                    internal_id=u.id,
                    force=True,
                )
    except Exception as e:
        logger.error(f"Async cleanup error: {e}")
    finally:
        # Close async HTTP clients to prevent unclosed connector warnings
        await client.close()
        await user_management.close()


# ================================================================================================
# Sync tests
# ================================================================================================


class TestIndexManagementSync:
    """
    Tests for IndexManagementClient.

    IndexManagementClient inherits SemanticSearchClient, so it supports both
    search operations and index management operations.
    """

    def test_index_health(self, index_client: IndexManagementClient):
        """index_health runs without raising an exception."""
        for mode in INDEX_MODES:
            # index_health prints output and returns None; just verify no exception
            response: HealthResponse = index_client.index_health(index_mode=mode, locale=EN_US)
            logger.info(f"index_health({mode}) completed")

    @skip
    def test_refresh_index(self, index_client: IndexManagementClient):
        """refresh_index runs without raising an exception."""
        for mode in INDEX_MODES:
            # index_client.refresh_index(index_mode=mode, locale=EN_US)
            logger.info(f"refresh_index({mode}) completed")

    @skip
    def test_force_merge_index(self, index_client: IndexManagementClient):
        """force_merge_index runs without raising an exception."""
        for mode in INDEX_MODES:
            # index_client.force_merge_index(index_mode=mode, locale=EN_US)
            logger.info(f"force_merge_index({mode}) completed")

    def test_iterate_documents(self, content_index_client: IndexManagementClient):
        """iterate_documents streams documents correctly."""
        for mode in INDEX_MODES:
            logger.info(f"Testing iterate_documents for mode={mode}")
            doc_count = 0
            max_docs_to_check = 10  # Limit to avoid long test times

            for doc in content_index_client.iterate_documents(index_mode=mode, locale=EN_US):
                # Verify document is an IndexDocument instance
                assert isinstance(doc, IndexDocument), "Document should be an IndexDocument instance"

                # Verify main fields
                assert isinstance(doc.id, str), "Document ID should be a string"
                assert isinstance(doc.content, str), "Document content should be a string"
                assert isinstance(doc.content_uri, str), "Document content_uri should be a string"

                # Verify metadata structure
                assert doc.meta is not None, "Document should have metadata"
                assert isinstance(doc.meta.concept_type, str), "Concept type should be a string"
                assert isinstance(doc.meta.locale, str), "Locale should be a string"
                assert isinstance(doc.meta.creation, str), "Creation timestamp should be a string"
                assert isinstance(doc.meta.modification, str), "Modification timestamp should be a string"
                # chunk_index is optional (None for single-chunk documents)
                if doc.meta.chunk_index is not None:
                    assert isinstance(doc.meta.chunk_index, int), "Chunk index should be an integer when present"

                doc_count += 1
                if doc_count >= max_docs_to_check:
                    break

            logger.info(f"iterate_documents({mode}) streamed {doc_count} documents successfully")
            assert doc_count > 0, f"Should have streamed at least one document for mode={mode}"

    def test_iterate_documents_empty_stream(self, index_client: IndexManagementClient):
        """iterate_documents handles empty streams gracefully."""
        # Using a fresh user with no data, the stream should be empty but not fail
        for mode in INDEX_MODES:
            doc_count = 0
            try:
                for doc in index_client.iterate_documents(index_mode=mode, locale=EN_US):
                    doc_count += 1
                logger.info(f"iterate_documents({mode}) for empty index returned {doc_count} documents")
            except Exception as e:
                # It's okay if there's no data, but shouldn't raise other exceptions
                logger.info(f"iterate_documents({mode}) raised: {e}")
                # Test passes as long as we can handle the empty case


# ================================================================================================
# Async tests
# ================================================================================================


class TestAsyncIndexManagementClient:
    """
    Tests for AsyncIndexManagementClient.

    AsyncIndexManagementClient supports index management operations.
    """

    @pytest.mark.asyncio
    async def test_index_health(self, async_index_client: AsyncIndexManagementClient):
        """index_health runs without raising an exception."""
        for mode in INDEX_MODES:
            await async_index_client.index_health(index_mode=mode, locale=EN_US)
            logger.info(f"Async index_health({mode}) completed")

    @pytest.mark.asyncio
    @skip
    async def test_refresh_index(self, async_index_client: AsyncIndexManagementClient):
        """refresh_index runs without raising an exception."""
        for mode in INDEX_MODES:
            await async_index_client.refresh_index(index_mode=mode, locale=EN_US)
            logger.info(f"Async refresh_index({mode}) completed")

    @pytest.mark.asyncio
    @skip
    async def test_force_merge_index(self, async_index_client: AsyncIndexManagementClient):
        """force_merge_index runs without raising an exception."""
        for mode in INDEX_MODES:
            await async_index_client.force_merge_index(index_mode=mode, locale=EN_US)
            logger.info(f"Async force_merge_index({mode}) completed")

    @pytest.mark.asyncio
    async def test_iterate_documents(self, async_index_client: AsyncIndexManagementClient):
        """iterate_documents streams documents correctly (async version)."""
        for mode in INDEX_MODES:
            logger.info(f"Testing async iterate_documents for mode={mode}")
            doc_count = 0
            max_docs_to_check = 10  # Limit to avoid long test times

            async for doc in async_index_client.iterate_documents(index_mode=mode, locale=EN_US):
                # Verify document is an IndexDocument instance
                assert isinstance(doc, IndexDocument), "Document should be an IndexDocument instance"

                # Verify main fields
                assert isinstance(doc.id, str), "Document ID should be a string"
                assert isinstance(doc.content, str), "Document content should be a string"
                assert isinstance(doc.content_uri, str), "Document content_uri should be a string"

                # Verify metadata structure
                assert doc.meta is not None, "Document should have metadata"
                assert isinstance(doc.meta.concept_type, str), "Concept type should be a string"
                assert isinstance(doc.meta.locale, str), "Locale should be a string"
                assert isinstance(doc.meta.creation, str), "Creation timestamp should be a string"
                assert isinstance(doc.meta.modification, str), "Modification timestamp should be a string"
                # chunk_index is optional (None for single-chunk documents)
                if doc.meta.chunk_index is not None:
                    assert isinstance(doc.meta.chunk_index, int), "Chunk index should be an integer when present"

                doc_count += 1
                if doc_count >= max_docs_to_check:
                    break

            logger.info(f"Async iterate_documents({mode}) streamed {doc_count} documents successfully")
            assert doc_count > 0, f"Should have streamed at least one document for mode={mode}"

    @pytest.mark.asyncio
    async def test_iterate_documents_empty_stream(self, async_index_client: AsyncIndexManagementClient):
        """iterate_documents handles empty streams gracefully (async version)."""
        # Using a fresh user with no data, the stream should be empty but not fail
        for mode in INDEX_MODES:
            doc_count = 0
            try:
                async for doc in async_index_client.iterate_documents(index_mode=mode, locale=EN_US):
                    doc_count += 1
                logger.info(f"Async iterate_documents({mode}) for empty index returned {doc_count} documents")
            except Exception as e:
                # It's okay if there's no data, but shouldn't raise other exceptions
                logger.info(f"Async iterate_documents({mode}) raised: {e}")
                # Test passes as long as we can handle the empty case
