# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the dedicated entity-descriptions endpoints (PKA-589).

``GET /v1/entity/{uri}/descriptions`` and ``PATCH /v1/entity/{uri}/descriptions`` are
declared in the GraphDataService OpenAPI specification (``graph.json``) with the
``DescriptionApiModel`` shape ``{"description": ..., "locale": ...}``.

These tests pin the **wire format** using a stub session. The observed *behaviour* of the
endpoints is confirmed against a live service in ``test_entity_descriptions.py``:

===============================  =====================================================
Body                             Effect
===============================  =====================================================
``descriptions`` key absent      no-op, answered with 204
``descriptions`` non-empty list  replace the whole set (unmentioned locales are dropped)
``descriptions`` empty list      delete every description of the entity
===============================  =====================================================
"""

from typing import Any, Dict, List, Optional

import pytest

from knowledge.base.entity import Description
from knowledge.base.language import DE_DE, EN_US
from knowledge.services.asyncio.base import ResponseData
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException
from knowledge.services.graph import WacomKnowledgeService

SERVICE_URL: str = "https://example.invalid"
ENTITY_URI: str = "wacom:core#0f1b2c3d"


class _StubRequest:
    """The subset of ``requests.PreparedRequest`` that error handling reads."""

    def __init__(self, method: str) -> None:
        self.method = method


class _StubResponse:
    def __init__(self, payload: Any, ok: bool = True, status_code: int = 200, method: str = "GET") -> None:
        self.__payload = payload
        self.ok = ok
        self.status_code = status_code
        self.content = b""
        self.text = ""
        self.url = f"{SERVICE_URL}/graph/v1/entity/{ENTITY_URI}/descriptions"
        self.request = _StubRequest(method)
        self.headers: Dict[str, str] = {}

    def json(self) -> Any:
        if self.status_code == 204:
            raise ValueError("204 has no body")
        return self.__payload


class _StubSession:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.payload: Any = {"descriptions": []}
        self.ok: bool = True
        self.status_code: int = 200

    def __record(self, method: str, url: str, kwargs: Dict[str, Any]) -> _StubResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        return _StubResponse(self.payload, ok=self.ok, status_code=self.status_code, method=method)

    def get(self, url: str, **kwargs: Any) -> _StubResponse:
        return self.__record("GET", url, kwargs)

    def patch(self, url: str, **kwargs: Any) -> _StubResponse:
        return self.__record("PATCH", url, kwargs)


class _StubAsyncSession:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.payload: Any = {"descriptions": []}
        self.ok: bool = True
        self.status: int = 200

    def __record(self, method: str, url: str, kwargs: Dict[str, Any]) -> ResponseData:
        self.calls.append({"method": method, "url": url, **kwargs})
        return ResponseData(ok=self.ok, status=self.status, content=self.payload, url=url, method=method)

    async def get(self, url: str, **kwargs: Any) -> ResponseData:
        return self.__record("GET", url, kwargs)

    async def patch(self, url: str, **kwargs: Any) -> ResponseData:
        return self.__record("PATCH", url, kwargs)


@pytest.fixture()
def stub_session(monkeypatch: pytest.MonkeyPatch) -> _StubSession:
    session: _StubSession = _StubSession()
    monkeypatch.setattr(WacomServiceAPIClient, "request_session", property(lambda self: session))
    return session


@pytest.fixture()
def stub_async_session(monkeypatch: pytest.MonkeyPatch) -> _StubAsyncSession:
    session: _StubAsyncSession = _StubAsyncSession()

    async def asyncio_session(self: AsyncWacomKnowledgeService) -> _StubAsyncSession:
        return session

    monkeypatch.setattr(AsyncWacomKnowledgeService, "asyncio_session", asyncio_session)
    return session


def _client() -> WacomKnowledgeService:
    return WacomKnowledgeService(service_url=SERVICE_URL)


def _async_client() -> AsyncWacomKnowledgeService:
    return AsyncWacomKnowledgeService(service_url=SERVICE_URL, application_name="unit-test")


# ------------------------------------------------ GET -----------------------------------------------------------------
def test_descriptions_reads_the_localized_descriptions(stub_session: _StubSession) -> None:
    """The response is parsed into Description objects, one per locale."""
    stub_session.payload = {
        "descriptions": [
            {"description": "A digital pen for creative professionals.", "locale": "en_US"},
            {"description": "Ein digitaler Stift für kreative Profis.", "locale": "de_DE"},
        ]
    }

    descriptions = _client().descriptions(ENTITY_URI)

    assert [(d.content, d.language_code) for d in descriptions] == [
        ("A digital pen for creative professionals.", EN_US),
        ("Ein digitaler Stift für kreative Profis.", DE_DE),
    ]


def test_descriptions_targets_the_dedicated_endpoint(stub_session: _StubSession) -> None:
    """The URI is addressed through the entity's own descriptions resource."""
    _client().descriptions(ENTITY_URI)

    call = stub_session.calls[-1]
    assert call["method"] == "GET"
    assert call["url"].endswith("/descriptions")
    assert "entity/" in call["url"]


def test_descriptions_of_an_entity_without_any_is_empty(stub_session: _StubSession) -> None:
    """An absent or empty key means the entity has no descriptions."""
    stub_session.payload = {}

    assert _client().descriptions(ENTITY_URI) == []


def test_descriptions_reports_a_service_error(stub_session: _StubSession) -> None:
    """A 404 for an unknown entity surfaces as a service exception."""
    stub_session.ok = False
    stub_session.status_code = 404
    stub_session.payload = {"title": "Not Found"}

    with pytest.raises(WacomServiceException):
        _client().descriptions(ENTITY_URI)


# ----------------------------------------------- PATCH ----------------------------------------------------------------
def test_update_descriptions_sends_a_non_empty_list(stub_session: _StubSession) -> None:
    """A non-empty list is sent under the ``descriptions`` key in the spec's shape."""
    stub_session.payload = {"descriptions": [{"description": "new", "locale": "en_US"}]}

    _client().update_descriptions(ENTITY_URI, [Description("new", EN_US)])

    call = stub_session.calls[-1]
    assert call["method"] == "PATCH"
    assert call["json"] == {"descriptions": [{"description": "new", "locale": EN_US}]}


def test_update_descriptions_returns_the_updated_list(stub_session: _StubSession) -> None:
    """The service answers with the descriptions it stored."""
    stub_session.payload = {"descriptions": [{"description": "new", "locale": "en_US"}]}

    updated = _client().update_descriptions(ENTITY_URI, [Description("new", EN_US)])

    assert [(d.content, d.language_code) for d in updated] == [("new", EN_US)]


def test_an_empty_list_requests_deletion_of_every_description(stub_session: _StubSession) -> None:
    """An empty list is meaningful: it clears the entity's descriptions."""
    _client().update_descriptions(ENTITY_URI, [])

    assert stub_session.calls[-1]["json"] == {"descriptions": []}


def test_none_omits_the_key_so_the_service_treats_it_as_a_no_op(stub_session: _StubSession) -> None:
    """``None`` must not be confused with an empty list — it leaves descriptions untouched."""
    stub_session.status_code = 204

    _client().update_descriptions(ENTITY_URI, None)

    assert stub_session.calls[-1]["json"] == {}


def test_a_no_op_update_returns_no_descriptions(stub_session: _StubSession) -> None:
    """A 204 carries no body, so nothing is parsed out of it."""
    stub_session.status_code = 204

    assert _client().update_descriptions(ENTITY_URI, None) == []


def test_update_descriptions_reports_a_service_error(stub_session: _StubSession) -> None:
    """A rejected update surfaces as a service exception."""
    stub_session.ok = False
    stub_session.status_code = 409
    stub_session.payload = {"title": "Conflict"}

    with pytest.raises(WacomServiceException):
        _client().update_descriptions(ENTITY_URI, [Description("new", EN_US)])


def test_descriptions_without_content_are_not_sent(stub_session: _StubSession) -> None:
    """Empty or blank descriptions are dropped, as they are for entity payloads."""
    _client().update_descriptions(ENTITY_URI, [Description("", EN_US), Description("keep", DE_DE)])

    assert stub_session.calls[-1]["json"] == {"descriptions": [{"description": "keep", "locale": DE_DE}]}


# --------------------------------------------- async mirror -----------------------------------------------------------
async def test_async_descriptions_reads_the_localized_descriptions(stub_async_session: _StubAsyncSession) -> None:
    """The async client parses the same payload."""
    stub_async_session.payload = {"descriptions": [{"description": "value", "locale": "en_US"}]}

    descriptions = await _async_client().descriptions(ENTITY_URI)

    assert [(d.content, d.language_code) for d in descriptions] == [("value", EN_US)]


async def test_async_update_descriptions_sends_the_same_body(stub_async_session: _StubAsyncSession) -> None:
    """Sync and async put the same three states on the wire."""
    stub_async_session.payload = {"descriptions": []}
    client: AsyncWacomKnowledgeService = _async_client()

    await client.update_descriptions(ENTITY_URI, [Description("new", EN_US)])
    replace: Optional[Dict[str, Any]] = stub_async_session.calls[-1]["json"]
    await client.update_descriptions(ENTITY_URI, [])
    clear: Optional[Dict[str, Any]] = stub_async_session.calls[-1]["json"]
    await client.update_descriptions(ENTITY_URI, None)
    noop: Optional[Dict[str, Any]] = stub_async_session.calls[-1]["json"]

    assert replace == {"descriptions": [{"description": "new", "locale": EN_US}]}
    assert clear == {"descriptions": []}
    assert noop == {}


async def test_async_update_descriptions_reports_a_service_error(stub_async_session: _StubAsyncSession) -> None:
    """A rejected update surfaces as a service exception."""
    stub_async_session.ok = False
    stub_async_session.status = 404

    with pytest.raises(WacomServiceException):
        await _async_client().update_descriptions(ENTITY_URI, [Description("new", EN_US)])
