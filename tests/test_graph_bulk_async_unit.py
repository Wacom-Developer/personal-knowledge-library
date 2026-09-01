# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the bulk entity paths of ``AsyncWacomKnowledgeService``.

The ``AsyncSession`` is replaced by a stub, so no server and no event-loop networking are
involved. These mirror ``tests/test_graph_bulk_unit.py`` to keep sync and async in step.
"""

from typing import Any, Dict, List

import pytest

from knowledge.base.language import EN_US
from knowledge.base.ontology import OntologyClassReference, ThingObject
from knowledge.services.asyncio.base import ResponseData
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.base import WacomServiceException

SERVICE_URL: str = "https://example.invalid"
PERSON: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")


class _StubAsyncSession:
    """Records the calls a client makes and answers them from a queue of payloads."""

    def __init__(self) -> None:
        self.posts: List[Dict[str, Any]] = []
        self.gets: List[Dict[str, Any]] = []
        self.post_payloads: List[Any] = []
        self.get_payloads: List[Any] = []
        self.post_ok: bool = True

    def __response(self, content: Any, method: str) -> ResponseData:
        return ResponseData(
            ok=self.post_ok if method == "POST" else True,
            status=200 if (self.post_ok or method != "POST") else 500,
            content=content,
            url=SERVICE_URL,
            method=method,
        )

    async def post(self, url: str, **kwargs: Any) -> ResponseData:
        self.posts.append({"url": url, **kwargs})
        return self.__response(self.post_payloads.pop(0) if self.post_payloads else {}, "POST")

    async def get(self, url: str, **kwargs: Any) -> ResponseData:
        self.gets.append({"url": url, **kwargs})
        return self.__response(self.get_payloads.pop(0) if self.get_payloads else [], "GET")


@pytest.fixture()
def stub_session(monkeypatch: pytest.MonkeyPatch) -> _StubAsyncSession:
    """Bind a recording stub session to every async client built in the test."""
    session: _StubAsyncSession = _StubAsyncSession()

    async def asyncio_session(self: AsyncWacomKnowledgeService) -> _StubAsyncSession:
        return session

    monkeypatch.setattr(AsyncWacomKnowledgeService, "asyncio_session", asyncio_session)
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


async def test_bulk_create_assigns_the_uri_the_service_returned(stub_session: _StubAsyncSession) -> None:
    """Baseline: every entity comes back carrying its new URI."""
    client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(
        service_url=SERVICE_URL, application_name="unit-test"
    )
    stub_session.post_payloads = [{"uris": ["uri-0", "uri-1"]}]

    created = await client.create_entity_bulk(_things(2), batch_size=10)

    assert [thing.uri for thing in created] == ["uri-0", "uri-1"]


async def test_bulk_create_reports_a_failed_batch(stub_session: _StubAsyncSession) -> None:
    """A rejected batch must raise, not be skipped silently.

    Swallowing it returns entities with no URI and no indication that nothing was written.
    """
    client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(
        service_url=SERVICE_URL, application_name="unit-test"
    )
    stub_session.post_ok = False
    stub_session.post_payloads = [{"message": "rejected"}]

    with pytest.raises(WacomServiceException):
        await client.create_entity_bulk(_things(2), batch_size=10)


async def test_bulk_create_keeps_the_uri_when_the_image_upload_fails(
    stub_session: _StubAsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed image upload must not cost the caller the URI of a created entity."""
    client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(
        service_url=SERVICE_URL, application_name="unit-test"
    )
    stub_session.post_payloads = [{"uris": ["uri-0", "uri-1"]}]

    async def failing_upload(*args: Any, **kwargs: Any) -> str:
        raise WacomServiceException("image service is down", status_code=500)

    monkeypatch.setattr(client, "set_entity_image_url", failing_upload)

    created = await client.create_entity_bulk(_things(2, with_image=True), batch_size=10)

    assert [thing.uri for thing in created] == ["uri-0", "uri-1"]


async def test_bulk_create_sends_one_request_per_batch(stub_session: _StubAsyncSession) -> None:
    """``batch_size`` governs how many entities travel in a single request."""
    client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(
        service_url=SERVICE_URL, application_name="unit-test"
    )
    stub_session.post_payloads = [{"uris": ["uri-0", "uri-1"]}, {"uris": ["uri-2"]}]

    created = await client.create_entity_bulk(_things(3), batch_size=2)

    assert [len(call["json"]) for call in stub_session.posts] == [2, 1]
    assert [thing.uri for thing in created] == ["uri-0", "uri-1", "uri-2"]


async def test_entities_chunks_large_uri_lists(stub_session: _StubAsyncSession) -> None:
    """The async client chunks URIs the same way the sync one does."""
    client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(
        service_url=SERVICE_URL, application_name="unit-test"
    )
    uris: List[str] = [f"uri-{idx}" for idx in range(250)]
    stub_session.get_payloads = [
        [_entity_payload(uri) for uri in uris[idx : idx + 100]] for idx in range(0, len(uris), 100)
    ]

    things = await client.entities(uris, batch_size=100)

    assert len(stub_session.gets) == 3
    assert [thing.uri for thing in things] == uris
