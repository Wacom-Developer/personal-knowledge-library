# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests pinning the query parameters the semantic-search calls put on the wire.

The GraphDataService binds ``[FromQuery] string locale`` on every ``/semantic-search/*``
endpoint (``SemanticSearchController``), and the OpenAPI specification agrees. A parameter
sent under any other name binds to ``null``, so the caller's locale is silently discarded
and the search runs unfiltered — a wrong result, not an error, which is why it needs a test
at the wire level rather than an integration test.

The HTTP layer is stubbed; no server required.
"""

from typing import Any, Dict, List

import pytest

from knowledge.base.language import EN_US
from knowledge.base.ontology import OntologyClassReference, OntologyPropertyReference
from knowledge.services.asyncio.base import ResponseData
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.base import WacomServiceAPIClient
from knowledge.services.graph import SearchPattern, WacomKnowledgeService

SERVICE_URL: str = "https://example.invalid"
PERSON: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")
BIRTH_DATE: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#birthDate")
IS_RELATED: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#isRelated")

# An empty but structurally valid semantic-search response.
EMPTY_RESULT: Dict[str, Any] = {"result": [], "nextPageId": None}


class _StubResponse:
    """Minimal stand-in for ``requests.Response``."""

    def __init__(self, payload: Any) -> None:
        self.__payload = payload
        self.ok = True
        self.status_code = 200
        self.content = b""

    def json(self) -> Any:
        return self.__payload


class _RecordingSession:
    """Captures the query parameters of every GET the client issues."""

    def __init__(self) -> None:
        self.gets: List[Dict[str, Any]] = []

    def get(self, url: str, **kwargs: Any) -> _StubResponse:
        self.gets.append({"url": url, **kwargs})
        return _StubResponse(EMPTY_RESULT)

    @property
    def last_params(self) -> Dict[str, Any]:
        return dict(self.gets[-1]["params"])


class _RecordingAsyncSession:
    """Async counterpart of ``_RecordingSession``."""

    def __init__(self) -> None:
        self.gets: List[Dict[str, Any]] = []

    async def get(self, url: str, **kwargs: Any) -> ResponseData:
        self.gets.append({"url": url, **kwargs})
        return ResponseData(ok=True, status=200, content=EMPTY_RESULT, url=url, method="GET")

    @property
    def last_params(self) -> Dict[str, Any]:
        return dict(self.gets[-1]["params"])


@pytest.fixture()
def sync_session(monkeypatch: pytest.MonkeyPatch) -> _RecordingSession:
    session: _RecordingSession = _RecordingSession()
    monkeypatch.setattr(WacomServiceAPIClient, "request_session", property(lambda self: session))
    return session


@pytest.fixture()
def async_session(monkeypatch: pytest.MonkeyPatch) -> _RecordingAsyncSession:
    session: _RecordingAsyncSession = _RecordingAsyncSession()

    async def asyncio_session(self: AsyncWacomKnowledgeService) -> _RecordingAsyncSession:
        return session

    monkeypatch.setattr(AsyncWacomKnowledgeService, "asyncio_session", asyncio_session)
    return session


def _sync_client() -> WacomKnowledgeService:
    return WacomKnowledgeService(service_url=SERVICE_URL)


def _async_client() -> AsyncWacomKnowledgeService:
    return AsyncWacomKnowledgeService(service_url=SERVICE_URL, application_name="unit-test")


# ------------------------------------------- sync client --------------------------------------------------------------
def test_search_labels_sends_the_locale(sync_session: _RecordingSession) -> None:
    """Baseline: this call already used the name the service binds."""
    _sync_client().search_labels(search_term="da Vinci", language_code=EN_US)

    assert sync_session.last_params["locale"] == EN_US


def test_search_description_sends_the_locale(sync_session: _RecordingSession) -> None:
    """Baseline: this call already used the name the service binds."""
    _sync_client().search_description(search_term="polymath", language_code=EN_US)

    assert sync_session.last_params["locale"] == EN_US


def test_search_all_sends_the_locale(sync_session: _RecordingSession) -> None:
    """``/semantic-search/types`` binds ``locale``, so ``language`` is discarded."""
    _sync_client().search_all(search_term="da Vinci", language_code=EN_US, types=[PERSON])

    assert sync_session.last_params["locale"] == EN_US
    assert "language" not in sync_session.last_params


def test_search_literal_sends_the_locale(sync_session: _RecordingSession) -> None:
    """``/semantic-search/literal`` binds ``locale``, so ``language`` is discarded."""
    _sync_client().search_literal(
        literal=BIRTH_DATE,
        search_term="1452",
        pattern=SearchPattern.REGEX,
        language_code=EN_US,
    )

    assert sync_session.last_params["locale"] == EN_US
    assert "language" not in sync_session.last_params


def test_search_relation_sends_the_locale(sync_session: _RecordingSession) -> None:
    """``/semantic-search/relation`` binds ``locale``, so ``language`` is discarded."""
    _sync_client().search_relation(
        subject_uri="uri-subject",
        relation=IS_RELATED,
        object_uri=None,
        language_code=EN_US,
    )

    assert sync_session.last_params["locale"] == EN_US
    assert "language" not in sync_session.last_params


def test_no_search_call_sends_a_language_parameter(sync_session: _RecordingSession) -> None:
    """Whole-surface guard: the service has no ``language`` parameter on any search."""
    client: WacomKnowledgeService = _sync_client()
    client.search_labels(search_term="x", language_code=EN_US)
    client.search_description(search_term="x", language_code=EN_US)
    client.search_all(search_term="x", language_code=EN_US, types=[PERSON])
    client.search_literal(literal=BIRTH_DATE, search_term="x", pattern=SearchPattern.REGEX, language_code=EN_US)
    client.search_relation(subject_uri="s", relation=IS_RELATED, object_uri=None, language_code=EN_US)

    assert [call for call in sync_session.gets if "language" in call["params"]] == []
    assert all("locale" in call["params"] for call in sync_session.gets)


# ------------------------------------------ async client --------------------------------------------------------------
async def test_async_search_all_sends_the_locale(async_session: _RecordingAsyncSession) -> None:
    """The async mirror carries the same parameter names."""
    await _async_client().search_all(search_term="da Vinci", language_code=EN_US, types=[PERSON])

    assert async_session.last_params["locale"] == EN_US
    assert "language" not in async_session.last_params


async def test_async_search_literal_sends_the_locale(async_session: _RecordingAsyncSession) -> None:
    """The async mirror carries the same parameter names."""
    await _async_client().search_literal(
        literal=BIRTH_DATE,
        search_term="1452",
        pattern=SearchPattern.REGEX,
        language_code=EN_US,
    )

    assert async_session.last_params["locale"] == EN_US
    assert "language" not in async_session.last_params


async def test_async_search_relation_sends_the_locale(async_session: _RecordingAsyncSession) -> None:
    """The async mirror carries the same parameter names."""
    await _async_client().search_relation(
        subject_uri="uri-subject",
        relation=IS_RELATED,
        object_uri=None,
        language_code=EN_US,
    )

    assert async_session.last_params["locale"] == EN_US
    assert "language" not in async_session.last_params
