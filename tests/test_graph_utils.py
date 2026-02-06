# -*- coding: utf-8 -*-
# Copyright © 2025-present Wacom. All rights reserved.
"""
Unit tests for knowledge/utils/graph.py

These tests verify the graph utility functions using mocked clients.
"""

import pytest
from typing import List
from unittest.mock import MagicMock, AsyncMock, PropertyMock

from knowledge.base.entity import Label
from knowledge.base.language import EN_US, LocaleCode
from knowledge.base.ontology import ThingObject, THING_CLASS, OntologyClassReference
from knowledge.services.graph import Visibility
from knowledge.utils.graph import (
    count_things,
    count_things_session,
    things_session_iter,
    things_iter,
    async_count_things,
    async_count_things_session,
    async_things_iter,
    async_things_session_iter,
)


def _create_mock_thing(uri: str, label: str = "Test") -> ThingObject:
    """Helper to create a mock ThingObject."""
    thing = ThingObject(
        uri=uri,
        label=[Label(label, EN_US, main=True)],
        owner=True,
    )
    return thing


class TestCountThings:
    """Tests for count_things function."""

    def test_count_things_returns_total(self):
        """Test that count_things returns the total count."""
        mock_client = MagicMock()
        mock_client.listing.return_value = ([], 42, None)

        result = count_things(
            wacom_client=mock_client,
            user_token="test-token",
            concept_type=THING_CLASS,
        )

        assert result == 42
        mock_client.listing.assert_called_once()

    def test_count_things_with_visibility(self):
        """Test count_things with visibility filter."""
        mock_client = MagicMock()
        mock_client.listing.return_value = ([], 10, None)

        result = count_things(
            wacom_client=mock_client,
            user_token="test-token",
            concept_type=THING_CLASS,
            visibility=Visibility.PUBLIC,
        )

        assert result == 10
        # Verify visibility was passed
        call_kwargs = mock_client.listing.call_args[1]
        assert call_kwargs["visibility"] == Visibility.PUBLIC

    def test_count_things_with_locale(self):
        """Test count_things with locale filter."""
        mock_client = MagicMock()
        mock_client.listing.return_value = ([], 5, None)

        result = count_things(
            wacom_client=mock_client,
            user_token="test-token",
            concept_type=THING_CLASS,
            locale=LocaleCode("de_DE"),
        )

        assert result == 5
        call_kwargs = mock_client.listing.call_args[1]
        assert call_kwargs["locale"] == LocaleCode("de_DE")

    def test_count_things_only_own(self):
        """Test count_things with only_own filter."""
        mock_client = MagicMock()
        mock_client.listing.return_value = ([], 3, None)

        result = count_things(
            wacom_client=mock_client,
            user_token="test-token",
            concept_type=THING_CLASS,
            only_own=True,
        )

        assert result == 3
        call_kwargs = mock_client.listing.call_args[1]
        assert call_kwargs["is_owner"] is True


class TestCountThingsSession:
    """Tests for count_things_session function."""

    def test_count_things_session_returns_total(self):
        """Test that count_things_session returns the total count."""
        mock_client = MagicMock()
        mock_client.listing.return_value = ([], 100, None)

        result = count_things_session(
            wacom_client=mock_client,
            concept_type=THING_CLASS,
        )

        assert result == 100

    def test_count_things_session_with_filters(self):
        """Test count_things_session with various filters."""
        mock_client = MagicMock()
        mock_client.listing.return_value = ([], 25, None)

        result = count_things_session(
            wacom_client=mock_client,
            concept_type=THING_CLASS,
            locale=EN_US,
            visibility=Visibility.PRIVATE,
            only_own=False,
        )

        assert result == 25


class TestThingsSessionIter:
    """Tests for things_session_iter function."""

    def test_things_session_iter_raises_without_session(self):
        """Test that ValueError is raised when no session is configured."""
        mock_client = MagicMock()
        mock_client.current_session = None

        with pytest.raises(ValueError, match="No session configured"):
            list(things_session_iter(mock_client, THING_CLASS))

    def test_things_session_iter_yields_things(self):
        """Test that things are yielded correctly."""
        mock_client = MagicMock()
        mock_client.current_session = MagicMock()  # Session exists

        thing1 = _create_mock_thing("wacom:entity:1", "Thing 1")
        thing2 = _create_mock_thing("wacom:entity:2", "Thing 2")

        # First call returns 2 things, second call returns empty (end)
        mock_client.listing.side_effect = [
            ([thing1, thing2], 2, None),
            ([], 0, None),
        ]
        mock_client.handle_token.return_value = ("token", "refresh")

        results = list(things_session_iter(mock_client, THING_CLASS))

        assert len(results) == 2
        assert results[0].uri == "wacom:entity:1"
        assert results[1].uri == "wacom:entity:2"

    def test_things_session_iter_handles_pagination(self):
        """Test that pagination works correctly."""
        mock_client = MagicMock()
        mock_client.current_session = MagicMock()

        thing1 = _create_mock_thing("wacom:entity:1")
        thing2 = _create_mock_thing("wacom:entity:2")
        thing3 = _create_mock_thing("wacom:entity:3")

        # Simulate pagination: first page returns 2 items with next_page_id
        # second page returns 1 item, third call returns empty
        mock_client.listing.side_effect = [
            ([thing1, thing2], 3, "page2"),
            ([thing3], 3, None),
            ([], 0, None),
        ]
        mock_client.handle_token.return_value = ("token", "refresh")

        results = list(things_session_iter(mock_client, THING_CLASS, fetch_size=2))

        assert len(results) == 3

    def test_things_session_iter_empty_result(self):
        """Test iterator with empty results."""
        mock_client = MagicMock()
        mock_client.current_session = MagicMock()
        mock_client.listing.return_value = ([], 0, None)

        results = list(things_session_iter(mock_client, THING_CLASS))

        assert len(results) == 0


class TestThingsIter:
    """Tests for things_iter function."""

    def test_things_iter_with_tokens(self):
        """Test things_iter using user tokens."""
        mock_client = MagicMock()

        thing1 = _create_mock_thing("wacom:entity:1")

        mock_client.listing.side_effect = [
            ([thing1], 1, None),
            ([], 0, None),
        ]
        mock_client.handle_token.return_value = ("new_token", "new_refresh")

        results = list(
            things_iter(
                mock_client,
                user_token="token",
                refresh_token="refresh",
                concept_type=THING_CLASS,
            )
        )

        assert len(results) == 1
        obj, user_token, refresh_token = results[0]
        assert obj.uri == "wacom:entity:1"
        mock_client.register_token.assert_called_once_with("token", "refresh")

    def test_things_iter_with_api_key_login(self):
        """Test things_iter using tenant API key login."""
        mock_client = MagicMock()

        thing1 = _create_mock_thing("wacom:entity:1")

        mock_client.listing.side_effect = [
            ([thing1], 1, None),
            ([], 0, None),
        ]
        mock_client.handle_token.return_value = ("token", "refresh")

        results = list(
            things_iter(
                mock_client,
                user_token="token",
                refresh_token="refresh",
                concept_type=THING_CLASS,
                tenant_api_key="api-key",
                external_user_id="user-123",
            )
        )

        assert len(results) == 1
        mock_client.login.assert_called_once_with(tenant_api_key="api-key", external_user_id="user-123")


class TestAsyncCountThings:
    """Tests for async_count_things function."""

    @pytest.mark.asyncio
    async def test_async_count_things_returns_total(self):
        """Test that async_count_things returns the total count."""
        mock_client = AsyncMock()
        mock_client.listing.return_value = ([], 50, None)

        result = await async_count_things(
            async_client=mock_client,
            user_token="test-token",
            concept_type=THING_CLASS,
        )

        assert result == 50

    @pytest.mark.asyncio
    async def test_async_count_things_with_filters(self):
        """Test async_count_things with filters."""
        mock_client = AsyncMock()
        mock_client.listing.return_value = ([], 15, None)

        result = await async_count_things(
            async_client=mock_client,
            user_token="test-token",
            concept_type=THING_CLASS,
            locale=EN_US,
            visibility=Visibility.PUBLIC,
            only_own=True,
        )

        assert result == 15


class TestAsyncCountThingsSession:
    """Tests for async_count_things_session function."""

    @pytest.mark.asyncio
    async def test_async_count_things_session_returns_total(self):
        """Test that async_count_things_session returns the total count."""
        mock_client = AsyncMock()
        mock_client.listing.return_value = ([], 75, None)

        result = await async_count_things_session(
            async_client=mock_client,
            concept_type=THING_CLASS,
        )

        assert result == 75


class TestAsyncThingsIter:
    """Tests for async_things_iter function."""

    @pytest.mark.asyncio
    async def test_async_things_iter_with_tokens(self):
        """Test async_things_iter using user tokens."""
        mock_client = AsyncMock()

        thing1 = _create_mock_thing("wacom:entity:1")

        mock_client.listing.side_effect = [
            ([thing1], 1, None),
            ([], 0, None),
        ]
        mock_client.handle_token.return_value = ("new_token", "new_refresh")

        results = []
        async for item in async_things_iter(
            mock_client,
            user_token="token",
            refresh_token="refresh",
            concept_type=THING_CLASS,
        ):
            results.append(item)

        assert len(results) == 1
        obj, user_token, refresh_token = results[0]
        assert obj.uri == "wacom:entity:1"

    @pytest.mark.asyncio
    async def test_async_things_iter_with_api_key_login(self):
        """Test async_things_iter using tenant API key login."""
        mock_client = AsyncMock()

        thing1 = _create_mock_thing("wacom:entity:1")

        mock_client.listing.side_effect = [
            ([thing1], 1, None),
            ([], 0, None),
        ]
        mock_client.handle_token.return_value = ("token", "refresh")

        results = []
        async for item in async_things_iter(
            mock_client,
            user_token="token",
            refresh_token="refresh",
            concept_type=THING_CLASS,
            tenant_api_key="api-key",
            external_user_id="user-123",
        ):
            results.append(item)

        assert len(results) == 1
        mock_client.login.assert_called_once_with(tenant_api_key="api-key", external_user_id="user-123")


class TestAsyncThingsSessionIter:
    """Tests for async_things_session_iter function."""

    @pytest.mark.asyncio
    async def test_async_things_session_iter_raises_without_session(self):
        """Test that ValueError is raised when no session is configured."""
        mock_client = AsyncMock()
        mock_client.current_session = None

        with pytest.raises(ValueError, match="No session configured"):
            async for _ in async_things_session_iter(mock_client, THING_CLASS):
                pass

    @pytest.mark.asyncio
    async def test_async_things_session_iter_yields_things(self):
        """Test that things are yielded correctly (async)."""
        mock_client = AsyncMock()
        mock_client.current_session = MagicMock()  # Session exists

        thing1 = _create_mock_thing("wacom:entity:1")
        thing2 = _create_mock_thing("wacom:entity:2")

        mock_client.listing.side_effect = [
            ([thing1, thing2], 2, None),
            ([], 0, None),
        ]
        mock_client.handle_token.return_value = ("token", "refresh")

        results = []
        async for item in async_things_session_iter(mock_client, THING_CLASS):
            results.append(item)

        assert len(results) == 2
        assert results[0].uri == "wacom:entity:1"
        assert results[1].uri == "wacom:entity:2"

    @pytest.mark.asyncio
    async def test_async_things_session_iter_only_own_filter(self):
        """Test only_own filter returns owned items."""
        mock_client = AsyncMock()
        mock_client.current_session = MagicMock()

        # Create thing with owner=True
        thing1 = _create_mock_thing("wacom:entity:1")

        mock_client.listing.side_effect = [
            ([thing1], 1, None),
            ([], 0, None),
        ]
        mock_client.handle_token.return_value = ("token", "refresh")

        results = []
        async for item in async_things_session_iter(mock_client, THING_CLASS, only_own=True):
            results.append(item)

        # Should include the thing since owner=True
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_async_things_session_iter_empty_result(self):
        """Test async iterator with empty results."""
        mock_client = AsyncMock()
        mock_client.current_session = MagicMock()
        mock_client.listing.return_value = ([], 0, None)

        results = []
        async for item in async_things_session_iter(mock_client, THING_CLASS):
            results.append(item)

        assert len(results) == 0
