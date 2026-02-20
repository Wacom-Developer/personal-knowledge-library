# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""
Integration tests for QueueManagementClient (sync) and AsyncQueueMonitorClient (async).

Requires environment variables:
    - INSTANCE: URL of the service instance
    - TENANT_API_KEY: Tenant API key for authentication

Queue endpoints require a TenantAdmin-role user.  The fixtures locate one automatically
by scanning all tenant users; tests are skipped if no such user exists.
"""

import os
from typing import List, Optional

import loguru
import pytest
import pytest_asyncio

from knowledge.base.queue import QueueNames, QueueCount, QueueMonitor
from knowledge.services.asyncio.queue_monitor import AsyncQueueMonitorClient
from knowledge.services.asyncio.users import AsyncUserManagementService
from knowledge.services.queue_management import QueueManagementClient
from knowledge.services.users import UserManagementServiceAPI, UserRole

logger = loguru.logger
LIMIT: int = 200


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


# ================================================================================================
# Sync fixtures
# ================================================================================================


@pytest.fixture(scope="module")
def queue_client():
    """
    Sync QueueManagementClient logged in as a TenantAdmin user.
    Queue endpoints require TenantAdmin role; tests are skipped if no such user exists.
    """
    instance_url = get_instance_url()
    tenant_api_key = get_tenant_api_key()

    user_management = UserManagementServiceAPI(service_url=instance_url)
    users = user_management.listing_users(tenant_api_key, limit=LIMIT)
    admin_external_id: Optional[str] = None
    for u in users:
        if UserRole.ADMIN in u.user_roles:
            admin_external_id = u.external_user_id
            break

    if not admin_external_id:
        pytest.skip("No TenantAdmin user found in tenant — queue endpoints require TenantAdmin role")

    client = QueueManagementClient(service_url=instance_url)
    client.login(tenant_api_key=tenant_api_key, external_user_id=admin_external_id)
    logger.info(f"Queue client logged in as TenantAdmin: {admin_external_id}")

    yield client


# ================================================================================================
# Async fixtures
# ================================================================================================


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def async_queue_client():
    """
    Async AsyncQueueMonitorClient logged in as a TenantAdmin user.
    Queue endpoints require TenantAdmin role; tests are skipped if no such user exists.
    """
    instance_url = get_instance_url()
    tenant_api_key = get_tenant_api_key()

    user_management = AsyncUserManagementService(service_url=instance_url)
    users = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    admin_external_id: Optional[str] = None
    for u in users:
        if UserRole.ADMIN in u.user_roles:
            admin_external_id = u.external_user_id
            break

    if not admin_external_id:
        pytest.skip("No TenantAdmin user found in tenant — queue endpoints require TenantAdmin role")

    client = AsyncQueueMonitorClient(service_url=instance_url)
    await client.login(tenant_api_key=tenant_api_key, external_user_id=admin_external_id)
    logger.info(f"Async queue client logged in as TenantAdmin: {admin_external_id}")

    yield client


# ================================================================================================
# Sync tests
# ================================================================================================


class TestQueueManagementSync:
    """Tests for the synchronous QueueManagementClient."""

    def test_list_queue_names(self, queue_client: QueueManagementClient):
        """Queue names endpoint returns a QueueNames object."""
        queue_names: QueueNames = queue_client.list_queue_names()
        assert queue_names is not None
        assert isinstance(queue_names.names, list)
        logger.info(f"Queue names: {queue_names.names}")

    def test_list_queues(self, queue_client: QueueManagementClient):
        """list_queues returns a list of QueueMonitor objects."""
        queues: List[QueueMonitor] = queue_client.list_queues()
        assert queues is not None
        assert isinstance(queues, list)
        for q in queues:
            assert q.name is not None

    def test_queue_is_empty(self, queue_client: QueueManagementClient):
        """queue_is_empty returns a bool for each known queue name."""
        queue_names: QueueNames = queue_client.list_queue_names()
        for name in queue_names.names:
            empty = queue_client.queue_is_empty(name)
            assert isinstance(empty, bool)
            logger.info(f"Queue '{name}' empty: {empty}")

    def test_queue_size(self, queue_client: QueueManagementClient):
        """queue_size returns a QueueCount with a non-negative count."""
        queue_names: QueueNames = queue_client.list_queue_names()
        for name in queue_names.names:
            size: QueueCount = queue_client.queue_size(name)
            assert size is not None
            assert size.count >= 0
            logger.info(f"Queue '{name}' size: {size.count}")

    def test_queue_monitor_information(self, queue_client: QueueManagementClient):
        """queue_monitor_information returns a QueueMonitor for each known queue."""
        queue_names: QueueNames = queue_client.list_queue_names()
        for name in queue_names.names:
            monitor: QueueMonitor = queue_client.queue_monitor_information(name)
            assert monitor is not None
            assert monitor.name is not None
            logger.info(f"Queue monitor '{name}': {monitor}")


# ================================================================================================
# Async tests
# ================================================================================================


class TestAsyncQueueMonitorClient:
    """Tests for the asynchronous AsyncQueueMonitorClient."""

    @pytest.mark.asyncio
    async def test_list_queue_names(self, async_queue_client: AsyncQueueMonitorClient):
        """Queue names endpoint returns a QueueNames object."""
        queue_names: QueueNames = await async_queue_client.list_queue_names()
        assert queue_names is not None
        assert isinstance(queue_names.names, list)
        logger.info(f"Async queue names: {queue_names.names}")

    @pytest.mark.asyncio
    async def test_list_queues(self, async_queue_client: AsyncQueueMonitorClient):
        """list_queues returns a list of QueueMonitor objects."""
        queues: List[QueueMonitor] = await async_queue_client.list_queues()
        assert queues is not None
        assert isinstance(queues, list)
        for q in queues:
            assert q.name is not None

    @pytest.mark.asyncio
    async def test_queue_is_empty(self, async_queue_client: AsyncQueueMonitorClient):
        """queue_is_empty returns a bool for each known queue name."""
        queue_names: QueueNames = await async_queue_client.list_queue_names()
        for name in queue_names.names:
            empty = await async_queue_client.queue_is_empty(name)
            assert isinstance(empty, bool)
            logger.info(f"Async queue '{name}' empty: {empty}")

    @pytest.mark.asyncio
    async def test_queue_size(self, async_queue_client: AsyncQueueMonitorClient):
        """queue_size returns a QueueCount with a non-negative count."""
        queue_names: QueueNames = await async_queue_client.list_queue_names()
        for name in queue_names.names:
            size: QueueCount = await async_queue_client.queue_size(name)
            assert size is not None
            assert size.count >= 0
            logger.info(f"Async queue '{name}' size: {size.count}")

    @pytest.mark.asyncio
    async def test_queue_monitor_information(self, async_queue_client: AsyncQueueMonitorClient):
        """queue_monitor_information returns a QueueMonitor for each known queue."""
        queue_names: QueueNames = await async_queue_client.list_queue_names()
        for name in queue_names.names:
            monitor: QueueMonitor = await async_queue_client.queue_monitor_information(name)
            assert monitor is not None
            assert monitor.name is not None
            logger.info(f"Async queue monitor '{name}': {monitor}")
