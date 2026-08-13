"""Unit tests for the RDF-import result models and the inflection level enum.

Pure model tests built from the OntologyManager OpenAPI schemas. No server required.
"""

from knowledge.base.ontology import (
    FailedImportResource,
    ImportedResource,
    ImportResponse,
    ImportValidation,
    InflectionLevel,
)


def test_inflection_level_values() -> None:
    assert InflectionLevel.LOW.value == "LOW"
    assert InflectionLevel.MID.value == "MID"
    assert InflectionLevel.HIGH.value == "HIGH"


def test_imported_resource_from_dict() -> None:
    resource = ImportedResource.from_dict({"name": "demo:creative#Artist", "type": "Class"})
    assert resource.name == "demo:creative#Artist"
    assert resource.resource_type == "Class"


def test_failed_import_resource_from_dict() -> None:
    failure = FailedImportResource.from_dict({"name": "demo:creative#Broken", "error": "unresolved range"})
    assert failure.name == "demo:creative#Broken"
    assert failure.error == "unresolved range"


def test_import_validation_handles_missing_and_null_lists() -> None:
    empty = ImportValidation.from_dict({})
    assert empty.imported == []
    assert empty.failed == []

    nulled = ImportValidation.from_dict({"imported": None, "failed": None})
    assert nulled.imported == []
    assert nulled.failed == []


def test_import_response_from_dict() -> None:
    payload = {
        "concepts": {
            "imported": [{"name": "demo:creative#Artist", "type": "Class"}],
            "failed": [],
        },
        "properties": {
            "imported": [],
            "failed": [{"name": "demo:creative#created", "error": "unknown domain"}],
        },
    }
    response = ImportResponse.from_dict(payload)

    assert len(response.concepts.imported) == 1
    assert response.concepts.imported[0].name == "demo:creative#Artist"
    assert response.concepts.failed == []
    assert response.properties.imported == []
    assert len(response.properties.failed) == 1
    assert response.properties.failed[0].error == "unknown domain"
