# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the bulk entity paths of ``WacomKnowledgeService``.

The HTTP layer is replaced by a stub session, so no server is required. These cover the
book-keeping around ``create_entity_bulk`` and the request chunking of ``entities``.
"""

from typing import Any, Dict, List, Optional

import pytest

from knowledge.base.language import EN_US
from knowledge.base.ontology import OntologyClassReference, ThingObject
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException
from knowledge.services.graph import ENTITY_URI_BATCH_SIZE, WacomKnowledgeService

SERVICE_URL: str = "https://example.invalid"
PERSON: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")


class _StubResponse:
    """Minimal stand-in for ``requests.Response``."""

    def __init__(self, payload: Any, ok: bool = True) -> None:
        self.__payload = payload
        self.ok = ok
        self.status_code = 200 if ok else 500
        self.content = b""

    def json(self) -> Any:
        return self.__payload


class _StubSession:
    """Records the calls a client makes and answers them from a queue of payloads."""

    def __init__(self) -> None:
        self.posts: List[Dict[str, Any]] = []
        self.gets: List[Dict[str, Any]] = []
        self.post_payloads: List[Any] = []
        self.get_payloads: List[Any] = []

    def post(self, url: str, **kwargs: Any) -> _StubResponse:
        self.posts.append({"url": url, **kwargs})
        return _StubResponse(self.post_payloads.pop(0) if self.post_payloads else {})

    def get(self, url: str, **kwargs: Any) -> _StubResponse:
        self.gets.append({"url": url, **kwargs})
        return _StubResponse(self.get_payloads.pop(0) if self.get_payloads else [])

    def patch(self, url: str, **kwargs: Any) -> _StubResponse:
        return _StubResponse({})


@pytest.fixture()
def stub_session(monkeypatch: pytest.MonkeyPatch) -> _StubSession:
    """Bind a recording stub session to every client built in the test."""
    session: _StubSession = _StubSession()
    monkeypatch.setattr(WacomServiceAPIClient, "request_session", property(lambda self: session))
    return session


def _things(count: int, with_image: bool = False) -> List[ThingObject]:
    entities: List[ThingObject] = []
    for idx in range(count):
        thing: ThingObject = ThingObject(concept_type=PERSON)
        thing.add_label(f"Person {idx}", EN_US)
        if with_image:
            thing.image = f"https://example.invalid/image-{idx}.png"
        entities.append(thing)
    return entities


# ------------------------------------------ create_entity_bulk --------------------------------------------------------
def test_bulk_create_assigns_the_uri_the_service_returned(stub_session: _StubSession) -> None:
    """Baseline: every entity comes back carrying its new URI."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    stub_session.post_payloads = [{"uris": ["uri-0", "uri-1"]}]

    created = client.create_entity_bulk(_things(2), batch_size=10)

    assert [thing.uri for thing in created] == ["uri-0", "uri-1"]


def test_bulk_create_keeps_the_uri_when_the_image_upload_fails(
    stub_session: _StubSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed image upload must not cost the caller the URI of a created entity.

    The entity exists server-side by then. Losing its URI leaves the caller unable to
    reference or clean it up, and a retry creates a duplicate.
    """
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    stub_session.post_payloads = [{"uris": ["uri-0", "uri-1"]}]

    def failing_upload(*args: Any, **kwargs: Any) -> str:
        raise WacomServiceException("image service is down", status_code=500)

    monkeypatch.setattr(client, "set_entity_image_url", failing_upload)

    created = client.create_entity_bulk(_things(2, with_image=True), batch_size=10)

    assert [thing.uri for thing in created] == ["uri-0", "uri-1"]


def test_bulk_create_sends_one_request_per_batch(stub_session: _StubSession) -> None:
    """``batch_size`` governs how many entities travel in a single request."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    stub_session.post_payloads = [{"uris": ["uri-0", "uri-1"]}, {"uris": ["uri-2"]}]

    created = client.create_entity_bulk(_things(3), batch_size=2)

    assert len(stub_session.posts) == 2
    assert [len(call["json"]) for call in stub_session.posts] == [2, 1]
    assert [thing.uri for thing in created] == ["uri-0", "uri-1", "uri-2"]


# --------------------------------------------- entities ---------------------------------------------------------------
def _entity_payload(uri: str) -> Dict[str, Any]:
    return {
        "uri": uri,
        "type": "wacom:core#Person",
        "image": "",
        "labels": [{"value": "Person", "locale": "en_US", "isMain": True}],
        "descriptions": [],
        "dataProperties": {},
        "objectProperties": {},
    }


def test_entities_chunks_large_uri_lists(stub_session: _StubSession) -> None:
    """URIs travel in the query string, so a long list must be split across requests.

    Sending 400 URIs in one query string overruns the URL limit of a typical gateway and
    comes back as a 414 rather than as entities.
    """
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    uris: List[str] = [f"uri-{idx}" for idx in range(250)]
    stub_session.get_payloads = [
        [_entity_payload(uri) for uri in uris[0:100]],
        [_entity_payload(uri) for uri in uris[100:200]],
        [_entity_payload(uri) for uri in uris[200:250]],
    ]

    things = client.entities(uris, batch_size=100)

    assert len(stub_session.gets) == 3
    assert [thing.uri for thing in things] == uris


def test_entities_sends_a_single_request_for_a_short_list(stub_session: _StubSession) -> None:
    """A list that fits stays a single round-trip."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    stub_session.get_payloads = [[_entity_payload("uri-0"), _entity_payload("uri-1")]]

    things = client.entities(["uri-0", "uri-1"])

    assert len(stub_session.gets) == 1
    assert [thing.uri for thing in things] == ["uri-0", "uri-1"]


def test_entities_returns_nothing_for_an_empty_request(stub_session: _StubSession) -> None:
    """No URIs means no request at all."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)

    assert client.entities([]) == []
    assert stub_session.gets == []


def test_entities_forwards_the_locale(stub_session: _StubSession) -> None:
    """The locale filter reaches every chunk."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    uris: List[str] = [f"uri-{idx}" for idx in range(150)]
    stub_session.get_payloads = [
        [_entity_payload(uri) for uri in uris[0:100]],
        [_entity_payload(uri) for uri in uris[100:150]],
    ]

    client.entities(uris, locale=EN_US, batch_size=100)

    locales: List[Optional[str]] = [call["params"].get("locale") for call in stub_session.gets]
    assert locales == [EN_US, EN_US]


def test_entities_uses_the_shared_default_batch_size(stub_session: _StubSession) -> None:
    """Without an explicit batch size the shared default applies, matching the async client."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    uris: List[str] = [f"uri-{idx}" for idx in range(ENTITY_URI_BATCH_SIZE * 2 + 1)]
    stub_session.get_payloads = [
        [_entity_payload(uri) for uri in uris[idx : idx + ENTITY_URI_BATCH_SIZE]]
        for idx in range(0, len(uris), ENTITY_URI_BATCH_SIZE)
    ]

    things = client.entities(uris)

    assert len(stub_session.gets) == 3
    assert [thing.uri for thing in things] == uris
