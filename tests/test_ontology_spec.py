"""Offline contract tests: OntologyService against the OntologyManager OpenAPI spec.

Each test asserts the HTTP verb, resolved URL, query parameters and request body the
client produces. The transport is replaced by a recording stub, so no network access and
no PKS stage are required — destructive operations are safe to cover here.
"""

from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import pytest

from knowledge.base.ontology import (
    Comment,
    DataPropertyType,
    InflectionLevel,
    OntologyClassReference,
    OntologyContext,
    OntologyLabel,
    OntologyPropertyReference,
)
from knowledge.services.base import WacomServiceException
from knowledge.services.ontology import OntologyService

SERVICE_URL: str = "https://example.invalid"
BASE_URL: str = f"{SERVICE_URL}/ontology/v1"
CONTEXT: str = "demo"

ARTIST: OntologyClassReference = OntologyClassReference("demo", "creative", "Artist")
ARTIST_QUOTED: str = "demo%3Acreative%23Artist"

CREATED: OntologyPropertyReference = OntologyPropertyReference("demo", "creative", "created")
CREATED_QUOTED: str = "demo%3Acreative%23created"
PRODUCED: OntologyPropertyReference = OntologyPropertyReference("demo", "creative", "produced")
PRODUCED_QUOTED: str = "demo%3Acreative%23produced"


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


CONTEXT_LIST_PAYLOAD: List[Dict[str, Any]] = [
    {
        "version": 1,
        "data": {
            "namespaceMap": None,
            "baseURI": "wacom:core#",
            "isLocked": False,
            "lockedAt": None,
            "id": "67d5c7c86021ceab94db4baa",
            "tenantId": "67d5c7c86c458fc47bc4f06b",
            "labels": [],
            "comments": [],
            "name": "core",
            "icon": None,
            "dateAdded": "2025-03-15T18:32:40.92Z",
            "dateModified": "0001-01-01T00:00:00Z",
            "context": "core",
            "orphaned": False,
        },
    }
]


def test_contexts_parses_the_list_envelope() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=CONTEXT_LIST_PAYLOAD))

    contexts = service.contexts()

    method, url, _ = service.stub.last
    assert method == "GET"
    assert url == f"{BASE_URL}/context"
    assert len(contexts) == 1
    assert contexts[0].context == "core"
    assert contexts[0].base_uri == "wacom:core#"
    assert contexts[0].id == "67d5c7c86021ceab94db4baa"
    assert contexts[0].tenant_id == "67d5c7c86c458fc47bc4f06b"
    assert contexts[0].version == 1
    assert contexts[0].orphaned is False


def test_context_returns_first_entry_of_the_list() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=CONTEXT_LIST_PAYLOAD))

    context = service.context()

    assert context is not None
    assert context.context == "core"


def test_context_returns_none_when_no_contexts_exist() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=[]))

    assert service.context() is None


def test_context_returns_none_on_error_response() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=500, text="boom"))

    assert service.context() is None


def test_contexts_raises_on_error_response() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=500, text="boom"))

    with pytest.raises(WacomServiceException):
        service.contexts()


def test_context_accepts_legacy_single_envelope() -> None:
    legacy = {"version": 3, "context": CONTEXT_LIST_PAYLOAD[0]["data"]}
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=legacy))

    context = service.context()

    assert context is not None
    assert context.context == "core"
    assert context.version == 3


def test_ontology_context_from_dict_rejects_envelope_without_payload() -> None:
    with pytest.raises(ValueError, match="data"):
        OntologyContext.from_dict({"version": 1})


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


def test_set_concept_metadata_puts_nel_metadata() -> None:
    service = _StubOntologyService()

    service.set_concept_metadata(CONTEXT, ARTIST, InflectionLevel.HIGH, case_sensitive=True)

    method, url, kwargs = service.stub.last
    assert method == "PUT"
    assert url == f"{BASE_URL}/context/{CONTEXT}/concepts/{ARTIST_QUOTED}/metadata"
    assert kwargs["json"] == {
        "concept": "demo:creative#Artist",
        "inflection": "HIGH",
        "caseSensitive": True,
    }


def test_context_metadata_omits_version_when_not_given() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=[]))

    service.context_metadata(CONTEXT)

    method, url, kwargs = service.stub.last
    assert method == "GET"
    assert url == f"{BASE_URL}/context/{CONTEXT}/metadata"
    assert kwargs.get("params") in (None, {})


def test_context_metadata_sends_version_when_given() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=[]))

    service.context_metadata(CONTEXT, version=3)

    _, _, kwargs = service.stub.last
    assert kwargs["params"] == {"version": 3}


def test_update_context_puts_to_named_context() -> None:
    service = _StubOntologyService()

    service.update_context(CONTEXT, base_uri="wacom:demo", icon="ctx.png")

    method, url, kwargs = service.stub.last
    assert method == "PUT"
    assert url == f"{BASE_URL}/context/{CONTEXT}"
    assert kwargs["json"]["baseUri"] == "wacom:demo#"
    assert kwargs["json"]["name"] == CONTEXT
    assert kwargs["json"]["icon"] == "ctx.png"
    assert kwargs["json"]["labels"] == []
    assert kwargs["json"]["comments"] == []


def test_update_context_includes_context_only_when_given() -> None:
    service = _StubOntologyService()
    service.update_context(CONTEXT)
    _, _, kwargs = service.stub.last
    assert "context" not in kwargs["json"]

    service = _StubOntologyService()
    service.update_context(CONTEXT, context="other")
    _, _, kwargs = service.stub.last
    assert kwargs["json"]["context"] == "other"


def test_reset_context_posts_to_reset() -> None:
    service = _StubOntologyService()

    service.reset_context(CONTEXT)

    method, url, _ = service.stub.last
    assert method == "POST"
    assert url == f"{BASE_URL}/context/{CONTEXT}/reset"


def test_context_diff_returns_payload() -> None:
    payload = {"added": ["demo:creative#Artist"], "removed": []}
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=payload))

    result = service.context_diff(CONTEXT)

    method, url, _ = service.stub.last
    assert method == "GET"
    assert url == f"{BASE_URL}/context/{CONTEXT}/diff"
    assert result == payload


def test_context_diff_raises_on_error_response() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=404, text="no such context"))

    with pytest.raises(WacomServiceException):
        service.context_diff(CONTEXT)


def test_update_property_patches_the_property_uri() -> None:
    service = _StubOntologyService()

    service.update_property(CONTEXT, CREATED, icon="rel.png", labels=[OntologyLabel("created", "en")])

    method, url, kwargs = service.stub.last
    assert method == "PATCH"
    assert url == f"{BASE_URL}/context/{CONTEXT}/properties/{CREATED_QUOTED}"
    assert kwargs["json"] == {
        "labels": [{"value": "created", "lang": "en"}],
        "comments": [],
        "icon": "rel.png",
    }


def test_rename_property_posts_to_rename_route() -> None:
    service = _StubOntologyService()

    service.rename_property(CONTEXT, CREATED, PRODUCED)

    method, url, _ = service.stub.last
    assert method == "POST"
    assert url == f"{BASE_URL}/context/{CONTEXT}/properties/{CREATED_QUOTED}/rename/{PRODUCED_QUOTED}"


def test_add_property_domains_sends_bare_array() -> None:
    service = _StubOntologyService()

    service.add_property_domains(CONTEXT, CREATED, [ARTIST])

    method, url, kwargs = service.stub.last
    assert method == "PATCH"
    assert url == f"{BASE_URL}/context/{CONTEXT}/properties/{CREATED_QUOTED}/domains/add"
    assert kwargs["json"] == ["demo:creative#Artist"]


def test_remove_property_domains_targets_remove_route() -> None:
    service = _StubOntologyService()

    service.remove_property_domains(CONTEXT, CREATED, [ARTIST])

    method, url, kwargs = service.stub.last
    assert method == "PATCH"
    assert url == f"{BASE_URL}/context/{CONTEXT}/properties/{CREATED_QUOTED}/domains/remove"
    assert kwargs["json"] == ["demo:creative#Artist"]


def test_add_property_ranges_resolves_class_references() -> None:
    service = _StubOntologyService()

    service.add_property_ranges(CONTEXT, CREATED, [ARTIST])

    method, url, kwargs = service.stub.last
    assert method == "PATCH"
    assert url == f"{BASE_URL}/context/{CONTEXT}/properties/{CREATED_QUOTED}/ranges/add"
    assert kwargs["json"] == ["demo:creative#Artist"]


def test_add_property_ranges_resolves_data_property_types() -> None:
    service = _StubOntologyService()

    service.add_property_ranges(CONTEXT, CREATED, [DataPropertyType.INTEGER])

    _, _, kwargs = service.stub.last
    assert kwargs["json"] == ["http://www.w3.org/2001/XMLSchema#integer"]


def test_remove_property_ranges_targets_remove_route() -> None:
    service = _StubOntologyService()

    service.remove_property_ranges(CONTEXT, CREATED, [DataPropertyType.STRING])

    method, url, kwargs = service.stub.last
    assert method == "PATCH"
    assert url == f"{BASE_URL}/context/{CONTEXT}/properties/{CREATED_QUOTED}/ranges/remove"
    assert kwargs["json"] == ["http://www.w3.org/2001/XMLSchema#string"]


def test_versions_omits_range_params_when_not_given() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=[]))

    result = service.versions(CONTEXT)

    method, url, kwargs = service.stub.last
    assert method == "GET"
    assert url == f"{BASE_URL}/context/{CONTEXT}/versions"
    assert kwargs["params"] == {}
    assert result == []


def test_versions_sends_start_and_end() -> None:
    payload = [{"version": 1}, {"version": 2}]
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=payload))

    result = service.versions(CONTEXT, start_at=1, end_at=2)

    _, _, kwargs = service.stub.last
    assert kwargs["params"] == {"startAt": 1, "endAt": 2}
    assert result == payload


def test_pending_version_returns_payload() -> None:
    payload = {"version": 7, "pending": True}
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=payload))

    result = service.pending_version(CONTEXT)

    method, url, _ = service.stub.last
    assert method == "GET"
    assert url == f"{BASE_URL}/context/{CONTEXT}/versions/pending"
    assert result == payload


def test_pending_version_raises_on_error_response() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=500, text="boom"))

    with pytest.raises(WacomServiceException):
        service.pending_version(CONTEXT)


def test_rdf_import_posts_multipart_and_parses_response() -> None:
    payload = {
        "concepts": {"imported": [{"name": "demo:creative#Artist", "type": "Class"}], "failed": []},
        "properties": {"imported": [], "failed": []},
    }
    service = _StubOntologyService(_FakeResponse(status_code=200, payload=payload))

    result = service.rdf_import(CONTEXT, "<rdf:RDF/>", file_name="demo.rdf")

    method, url, kwargs = service.stub.last
    assert method == "POST"
    assert url == f"{BASE_URL}/context/{CONTEXT}/versions/rdf"
    assert kwargs["ignore_content_type"] is True
    assert kwargs["files"] == {"file": ("demo.rdf", b"<rdf:RDF/>")}
    assert result.concepts.imported[0].name == "demo:creative#Artist"
    assert result.properties.imported == []


def test_rdf_import_accepts_bytes_unchanged() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=200, payload={}))

    service.rdf_import(CONTEXT, b"\x00binary")

    _, _, kwargs = service.stub.last
    assert kwargs["files"] == {"file": ("ontology.rdf", b"\x00binary")}


def test_rdf_import_raises_on_error_response() -> None:
    service = _StubOntologyService(_FakeResponse(status_code=400, text="bad rdf"))

    with pytest.raises(WacomServiceException):
        service.rdf_import(CONTEXT, "<rdf:RDF/>")
