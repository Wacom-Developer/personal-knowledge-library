"""Unit tests for the ontology-update status and the tenant-vs-base diff models.

Both payloads are documented in the PKA-531 release notes of the ontology service:
``GET /v1/ontology-update/status`` (GraphDataService) and ``GET /v1/context/{name}/diff``
(OntologyManager). No server required.
"""

from datetime import datetime, timezone

from knowledge.base.ontology import (
    AddedConcept,
    AddedProperty,
    DataPropertyType,
    ModifiedBaseProperty,
    OntologyClassReference,
    OntologyDiff,
    OntologyPropertyReference,
    OntologyUpdateState,
    OntologyUpdateStatus,
    PropertyType,
)

LIFECYCLE_CLASS: OntologyClassReference = OntologyClassReference.parse("wacom:core#E2ELifecycle")
LIFECYCLE_DETAIL: OntologyClassReference = OntologyClassReference.parse("wacom:core#E2ELifecycleDetail")
THING: OntologyClassReference = OntologyClassReference.parse("wacom:core#Thing")
CODE_NAME: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#e2eCodeName")
IS_RELATED: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#isRelated")


# ------------------------------------------ Update status -------------------------------------------------------------
def test_update_status_parses_an_idle_tenant() -> None:
    status = OntologyUpdateStatus.from_dict(
        {
            "status": "NoUpdateInProgress",
            "ontologyName": "core",
            "previousOntologyVersion": 3,
            "appliedOntologyVersion": 4,
            "dateAdded": "2026-08-31T10:29:42.1946908+00:00",
            "dateModified": "2026-08-31T10:29:45.07Z",
        }
    )

    assert status.state is OntologyUpdateState.NO_UPDATE_IN_PROGRESS
    assert status.status == "NoUpdateInProgress"
    assert status.ontology_name == "core"
    assert status.previous_ontology_version == 3
    assert status.applied_ontology_version == 4
    assert status.date_added == datetime(2026, 8, 31, 10, 29, 42, 194690, tzinfo=timezone.utc)
    assert status.date_modified == datetime(2026, 8, 31, 10, 29, 45, 70000, tzinfo=timezone.utc)


def test_idle_status_is_neither_pending_nor_failed() -> None:
    status = OntologyUpdateStatus.from_dict({"status": "NoUpdateInProgress"})

    assert status.is_idle is True
    assert status.is_pending is False
    assert status.has_failed is False


def test_pending_status_reports_an_update_in_flight() -> None:
    status = OntologyUpdateStatus.from_dict({"status": "Pending"})

    assert status.state is OntologyUpdateState.PENDING
    assert status.is_pending is True
    assert status.is_idle is False
    assert status.has_failed is False


def test_failed_status_reports_a_failure() -> None:
    status = OntologyUpdateStatus.from_dict({"status": "Failed"})

    assert status.state is OntologyUpdateState.FAILED
    assert status.has_failed is True
    assert status.is_idle is False
    assert status.is_pending is False


def test_update_status_tolerates_a_state_it_does_not_know() -> None:
    status = OntologyUpdateStatus.from_dict({"status": "SomethingNew"})

    # An unrecognised state must not raise; the raw value stays available.
    assert status.state is None
    assert status.status == "SomethingNew"
    assert status.is_idle is False
    assert status.is_pending is False
    assert status.has_failed is False


def test_update_status_tolerates_a_sparse_payload() -> None:
    status = OntologyUpdateStatus.from_dict({})

    assert status.status == ""
    assert status.state is None
    assert status.ontology_name is None
    assert status.previous_ontology_version is None
    assert status.applied_ontology_version is None
    assert status.date_added is None
    assert status.date_modified is None


# --------------------------------------------- Diff -------------------------------------------------------------------
def test_diff_parses_added_concepts() -> None:
    diff = OntologyDiff.from_dict({"addedConcepts": [{"name": LIFECYCLE_CLASS.iri, "subClassOf": THING.iri}]})

    assert len(diff.added_concepts) == 1
    concept: AddedConcept = diff.added_concepts[0]
    assert concept.reference == LIFECYCLE_CLASS
    assert concept.subclass_of == THING


def test_diff_parses_an_added_data_property() -> None:
    diff = OntologyDiff.from_dict(
        {
            "addedProperties": [
                {
                    "name": CODE_NAME.iri,
                    "kind": "Literal",
                    "domains": [LIFECYCLE_CLASS.iri],
                    "ranges": [DataPropertyType.STRING.value],
                }
            ]
        }
    )

    prop: AddedProperty = diff.added_properties[0]
    assert prop.reference == CODE_NAME
    assert prop.kind is PropertyType.DATA_PROPERTY
    assert prop.domains == [LIFECYCLE_CLASS]
    assert [entry.iri for entry in prop.ranges] == [DataPropertyType.STRING.value]


def test_diff_parses_an_added_object_property() -> None:
    diff = OntologyDiff.from_dict(
        {
            "addedProperties": [
                {
                    "name": "wacom:core#e2eLinkedTo",
                    "kind": "Relation",
                    "domains": [LIFECYCLE_CLASS.iri],
                    "ranges": [LIFECYCLE_DETAIL.iri],
                }
            ]
        }
    )

    prop: AddedProperty = diff.added_properties[0]
    assert prop.kind is PropertyType.OBJECT_PROPERTY
    assert prop.ranges == [LIFECYCLE_DETAIL]


def test_diff_parses_modified_base_properties() -> None:
    diff = OntologyDiff.from_dict(
        {
            "modifiedBaseProperties": [
                {
                    "name": IS_RELATED.iri,
                    "kind": "Relation",
                    "addedDomains": [LIFECYCLE_CLASS.iri],
                    "addedRanges": [LIFECYCLE_DETAIL.iri],
                }
            ]
        }
    )

    modified: ModifiedBaseProperty = diff.modified_base_properties[0]
    assert modified.reference == IS_RELATED
    assert modified.kind is PropertyType.OBJECT_PROPERTY
    assert modified.added_domains == [LIFECYCLE_CLASS]
    assert modified.added_ranges == [LIFECYCLE_DETAIL]


def test_diff_of_a_pristine_tenant_is_empty() -> None:
    diff = OntologyDiff.from_dict({"addedConcepts": [], "addedProperties": [], "modifiedBaseProperties": []})

    assert diff.is_empty is True
    assert diff.added_concepts == []
    assert diff.added_properties == []
    assert diff.modified_base_properties == []


def test_diff_tolerates_missing_and_null_lists() -> None:
    assert OntologyDiff.from_dict({}).is_empty is True
    nulled = OntologyDiff.from_dict({"addedConcepts": None, "addedProperties": None, "modifiedBaseProperties": None})
    assert nulled.is_empty is True


def test_diff_is_not_empty_when_only_a_base_property_was_customized() -> None:
    diff = OntologyDiff.from_dict(
        {
            "modifiedBaseProperties": [
                {"name": IS_RELATED.iri, "kind": "Relation", "addedDomains": [LIFECYCLE_CLASS.iri], "addedRanges": []}
            ]
        }
    )

    assert diff.is_empty is False


def test_diff_concept_without_a_superclass_reports_none() -> None:
    diff = OntologyDiff.from_dict({"addedConcepts": [{"name": LIFECYCLE_CLASS.iri, "subClassOf": None}]})

    assert diff.added_concepts[0].subclass_of is None
