"""Offline contract tests for the ontology-update endpoints of the graph clients.

``PATCH /v1/ontology-update`` only *accepts* an apply - the work continues in the
background while the tenant is locked - so ``GET /v1/ontology-update/status`` is how a
caller learns that it finished. Both clients are covered, since the sync and async graph
clients must stay in parity. The transport is replaced by a recording stub, so no network
access and no PKS stage are required.
"""

from typing import Any, Dict, List, Optional, Tuple

import pytest

from knowledge.base.ontology import OntologyUpdateState, OntologyUpdateStatus
from knowledge.services.asyncio.base import ResponseData
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService

SERVICE_URL: str = "https://example.invalid"
BASE_URL: str = f"{SERVICE_URL}/graph/v1"

IDLE_PAYLOAD: Dict[str, Any] = {
    "status": "NoUpdateInProgress",
    "ontologyName": "core",
    "previousOntologyVersion": 3,
    "appliedOntologyVersion": 4,
    "dateAdded": "2026-08-31T10:29:42.1946908+00:00",
    "dateModified": "2026-08-31T10:29:45.07Z",
}


# ------------------------------------------- Sync harness -------------------------------------------------------------
class _FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, status_code: int = 200, payload: Any = None, text: str = "") -> None:
        self.status_code: int = status_code
        self.ok: bool = 200 <= status_code < 300
        self.text: str = text
        self.url: str = ""
        self.request: Any = type("_Request", (), {"method": ""})()
        self._payload: Any = payload

    def json(self) -> Any:
        return self._payload


class _RecordingSession:
    """Captures outgoing requests and returns a canned response."""

    def __init__(self, response: _FakeResponse) -> None:
        self.response: _FakeResponse = response
        self.calls: List[Tuple[str, str, Dict[str, Any]]] = []

    def _record(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append((method, url, kwargs))
        return self.response

    def get(self, url: str, **kwargs: Any) -> _FakeResponse:
        return self._record("GET", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> _FakeResponse:
        return self._record("PATCH", url, **kwargs)

    @property
    def last(self) -> Tuple[str, str, Dict[str, Any]]:
        """Most recent (method, url, kwargs) triple."""
        assert self.calls, "no request was issued"
        return self.calls[-1]


class _StubKnowledgeService(WacomKnowledgeService):
    """WacomKnowledgeService whose transport is replaced by a recording stub."""

    def __init__(self, response: Optional[_FakeResponse] = None) -> None:
        super().__init__(service_url=SERVICE_URL)
        self.stub: _RecordingSession = _RecordingSession(response or _FakeResponse())

    @property
    def request_session(self) -> Any:
        return self.stub


# ------------------------------------------ Async harness -------------------------------------------------------------
class _RecordingAsyncSession:
    """Captures outgoing async requests and returns a canned ResponseData."""

    def __init__(self, response: ResponseData) -> None:
        self.response: ResponseData = response
        self.calls: List[Tuple[str, str, Dict[str, Any]]] = []

    async def _record(self, method: str, url: str, **kwargs: Any) -> ResponseData:
        self.calls.append((method, url, kwargs))
        return self.response

    async def get(self, url: str, **kwargs: Any) -> ResponseData:
        return await self._record("GET", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> ResponseData:
        return await self._record("PATCH", url, **kwargs)

    @property
    def last(self) -> Tuple[str, str, Dict[str, Any]]:
        """Most recent (method, url, kwargs) triple."""
        assert self.calls, "no request was issued"
        return self.calls[-1]


class _StubAsyncKnowledgeService(AsyncWacomKnowledgeService):
    """AsyncWacomKnowledgeService whose transport is replaced by a recording stub."""

    def __init__(self, response: Optional[ResponseData] = None) -> None:
        super().__init__(service_url=SERVICE_URL, application_name="offline contract test")
        self.stub: _RecordingAsyncSession = _RecordingAsyncSession(
            response or ResponseData(ok=True, status=200, content=IDLE_PAYLOAD, url="", method="GET")
        )

    async def asyncio_session(self) -> Any:
        return self.stub


def _async_response(status: int = 200, content: Any = None) -> ResponseData:
    """Build a ResponseData for the async stub."""
    return ResponseData(ok=200 <= status < 300, status=status, content=content, url="", method="GET")


# --------------------------------------- Sync: update status ----------------------------------------------------------
def test_ontology_update_status_gets_the_status_route() -> None:
    service = _StubKnowledgeService(_FakeResponse(status_code=200, payload=IDLE_PAYLOAD))

    result = service.ontology_update_status()

    method, url, _ = service.stub.last
    assert method == "GET"
    assert url == f"{BASE_URL}/ontology-update/status"
    assert isinstance(result, OntologyUpdateStatus)


def test_ontology_update_status_parses_the_payload() -> None:
    service = _StubKnowledgeService(_FakeResponse(status_code=200, payload=IDLE_PAYLOAD))

    result = service.ontology_update_status()

    assert result.state is OntologyUpdateState.NO_UPDATE_IN_PROGRESS
    assert result.is_idle is True
    assert result.ontology_name == "core"
    assert result.applied_ontology_version == 4


def test_ontology_update_status_reports_a_failed_apply() -> None:
    service = _StubKnowledgeService(_FakeResponse(status_code=200, payload={"status": "Failed"}))

    assert service.ontology_update_status().has_failed is True


def test_ontology_update_status_raises_on_error_response() -> None:
    service = _StubKnowledgeService(_FakeResponse(status_code=500, text="boom"))

    with pytest.raises(WacomServiceException):
        service.ontology_update_status()


def test_ontology_update_patches_the_update_route() -> None:
    service = _StubKnowledgeService(_FakeResponse(status_code=200))

    service.ontology_update()

    method, url, _ = service.stub.last
    assert method == "PATCH"
    assert url == f"{BASE_URL}/ontology-update"


def test_ontology_update_fix_patches_the_fix_route() -> None:
    service = _StubKnowledgeService(_FakeResponse(status_code=200))

    service.ontology_update(fix=True)

    _, url, _ = service.stub.last
    assert url == f"{BASE_URL}/ontology-update/fix"


# --------------------------------------- Async: update status ---------------------------------------------------------
async def test_async_ontology_update_status_gets_the_status_route() -> None:
    service = _StubAsyncKnowledgeService(_async_response(200, IDLE_PAYLOAD))

    result = await service.ontology_update_status()

    method, url, _ = service.stub.last
    assert method == "GET"
    assert url == f"{BASE_URL}/ontology-update/status"
    assert isinstance(result, OntologyUpdateStatus)
    assert result.is_idle is True
    assert result.applied_ontology_version == 4


async def test_async_ontology_update_status_reports_a_pending_apply() -> None:
    service = _StubAsyncKnowledgeService(_async_response(200, {"status": "Pending"}))

    result = await service.ontology_update_status()

    assert result.is_pending is True
    assert result.is_idle is False


async def test_async_ontology_update_status_raises_on_error_response() -> None:
    service = _StubAsyncKnowledgeService(_async_response(500, "boom"))

    with pytest.raises(WacomServiceException):
        await service.ontology_update_status()
