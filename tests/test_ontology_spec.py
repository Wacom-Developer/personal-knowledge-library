"""Offline contract tests: OntologyService against the OntologyManager OpenAPI spec.

Each test asserts the HTTP verb, resolved URL, query parameters and request body the
client produces. The transport is replaced by a recording stub, so no network access and
no PKS stage are required — destructive operations are safe to cover here.
"""

from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import pytest

from knowledge.base.ontology import Comment, OntologyClassReference, OntologyLabel
from knowledge.services.base import WacomServiceException
from knowledge.services.ontology import OntologyService

SERVICE_URL: str = "https://example.invalid"
BASE_URL: str = f"{SERVICE_URL}/ontology/v1"
CONTEXT: str = "demo"

ARTIST: OntologyClassReference = OntologyClassReference("demo", "creative", "Artist")
ARTIST_QUOTED: str = "demo%3Acreative%23Artist"


class _FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, status_code: int = 204, payload: Any = None, text: str = "") -> None:
        self.status_code: int = status_code
        self.ok: bool = 200 <= status_code < 300
        self.text: str = text
        self.url: str = ""
        self.request: Any = SimpleNamespace(method="")
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

    def post(self, url: str, **kwargs: Any) -> _FakeResponse:
        return self._record("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> _FakeResponse:
        return self._record("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> _FakeResponse:
        return self._record("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> _FakeResponse:
        return self._record("DELETE", url, **kwargs)

    @property
    def last(self) -> Tuple[str, str, Dict[str, Any]]:
        """Most recent (method, url, kwargs) triple."""
        assert self.calls, "no request was issued"
        return self.calls[-1]


class _StubOntologyService(OntologyService):
    """OntologyService whose transport is replaced by a recording stub."""

    def __init__(self, response: Optional[_FakeResponse] = None) -> None:
        super().__init__(service_url=SERVICE_URL)
        self.stub: _RecordingSession = _RecordingSession(response or _FakeResponse())

    @property
    def request_session(self) -> Any:
        return self.stub


def test_update_concept_patches_the_concept_uri() -> None:
    service = _StubOntologyService()

    service.update_concept(
        CONTEXT,
        ARTIST,
        icon="icon.png",
        labels=[OntologyLabel("Artist", "en")],
        comments=[Comment("A creator", "en")],
    )

    method, url, kwargs = service.stub.last
    assert method == "PATCH"
    assert url == f"{BASE_URL}/context/{CONTEXT}/concepts/{ARTIST_QUOTED}"
    assert kwargs["json"] == {
        "labels": [{"value": "Artist", "lang": "en"}],
        "comments": [{"value": "A creator", "lang": "en"}],
        "icon": "icon.png",
    }


def test_update_concept_sends_no_name_or_subclass_of() -> None:
    service = _StubOntologyService()

    service.update_concept(CONTEXT, ARTIST)

    _, _, kwargs = service.stub.last
    assert "name" not in kwargs["json"]
    assert "subClassOf" not in kwargs["json"]


def test_update_concept_raises_on_error_response() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=404, text="not found"))

    with pytest.raises(WacomServiceException):
        service.update_concept(CONTEXT, ARTIST)
