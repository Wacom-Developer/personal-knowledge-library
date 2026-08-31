"""Unit tests for the pending-ontology-version response model.

The ``GET /context/{name}/versions/pending`` endpoint has no response schema in the
OntologyManager OpenAPI specification. The fixture below is a verbatim capture from the
stage service: a **list** of change records, each carrying the changed element as a JSON
string in ``body`` with PascalCase keys. No server required.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from knowledge.base.ontology import (
    DataPropertyType,
    OntologyChangeOperation,
    OntologyChangeRecord,
    OntologyClass,
    OntologyClassReference,
    OntologyElementKind,
    OntologyProperty,
    OntologyPropertyReference,
    PendingOntologyVersion,
    PropertyType,
)

TENANT_ID: str = "6a95578d750b9cb0283eddb4"

# Verbatim capture of a pending version holding two concepts, two data properties
# ("literals"), two object properties ("relations") and one relation change.
PENDING_PAYLOAD: List[Dict[str, Any]] = [
    {
        "body": '{"Data":{"SubClassOf":"wacom:core#Thing","Id":"6a955796cc125f3279246fa8",'
        '"TenantId":"6a95578d750b9cb0283eddb4","Labels":[{"Value":"E2E lifecycle class","Lang":"en"},'
        '{"Value":"E2E-Lebenszyklus-Klasse","Lang":"de"}],'
        '"Comments":[{"Value":"Temporary class created by the ontology lifecycle test.","Lang":"en"}],'
        '"Name":"wacom:core#E2ELifecycle","Icon":null,"DateAdded":"2026-08-31T10:29:42.1946908+00:00",'
        '"DateModified":"0001-01-01T00:00:00","Context":"core","Orphaned":false}}',
        "context": "core",
        "kind": "INSERT_CONCEPT",
        "tenantId": TENANT_ID,
        "timeStamp": "2026-08-31T10:29:42.298Z",
        "version": 2,
    },
    {
        "body": '{"Data":{"SubClassOf":"wacom:core#E2ELifecycle","Id":"6a955796cc125f3279246fab",'
        '"TenantId":"6a95578d750b9cb0283eddb4","Labels":[{"Value":"E2E lifecycle detail","Lang":"en"}],'
        '"Comments":[],"Name":"wacom:core#E2ELifecycleDetail","Icon":null,'
        '"DateAdded":"2026-08-31T10:29:42.8387485+00:00","DateModified":"0001-01-01T00:00:00",'
        '"Context":"core","Orphaned":false}}',
        "context": "core",
        "kind": "INSERT_CONCEPT",
        "tenantId": TENANT_ID,
        "timeStamp": "2026-08-31T10:29:43.024Z",
        "version": 2,
    },
    {
        "body": '{"Data":{"Kind":1,"SubPropertyOf":null,"InverseOf":null,"Domains":["wacom:core#E2ELifecycle"],'
        '"Ranges":["http://www.w3.org/2001/XMLSchema#string"],"Id":"6a955797cc125f3279246fad",'
        '"TenantId":"6a95578d750b9cb0283eddb4","Labels":[{"Value":"Code name","Lang":"en"}],'
        '"Comments":[{"Value":"Free-text code name of the entity.","Lang":"en"}],'
        '"Name":"wacom:core#e2eCodeName","Icon":null,"DateAdded":"2026-08-31T10:29:43.5717419+00:00",'
        '"DateModified":"0001-01-01T00:00:00","Context":"core","Orphaned":false}}',
        "context": "core",
        "kind": "INSERT_LITERAL",
        "tenantId": TENANT_ID,
        "timeStamp": "2026-08-31T10:29:43.594Z",
        "version": 2,
    },
    {
        "body": '{"Data":{"Kind":1,"SubPropertyOf":null,"InverseOf":null,"Domains":["wacom:core#E2ELifecycle"],'
        '"Ranges":["http://www.w3.org/2001/XMLSchema#integer"],"Id":"6a955797cc125f3279246fae",'
        '"TenantId":"6a95578d750b9cb0283eddb4","Labels":[{"Value":"Revision","Lang":"en"}],"Comments":[],'
        '"Name":"wacom:core#e2eRevision","Icon":null,"DateAdded":"2026-08-31T10:29:43.799265+00:00",'
        '"DateModified":"0001-01-01T00:00:00","Context":"core","Orphaned":false}}',
        "context": "core",
        "kind": "INSERT_LITERAL",
        "tenantId": TENANT_ID,
        "timeStamp": "2026-08-31T10:29:43.822Z",
        "version": 2,
    },
    {
        "body": '{"Data":{"Kind":0,"SubPropertyOf":null,"InverseOf":null,"Domains":["wacom:core#E2ELifecycle"],'
        '"Ranges":["wacom:core#E2ELifecycleDetail"],"Id":"6a955798cc125f3279246faf",'
        '"TenantId":"6a95578d750b9cb0283eddb4","Labels":[{"Value":"linked to","Lang":"en"}],'
        '"Comments":[{"Value":"Links a lifecycle entity to one of its details.","Lang":"en"}],'
        '"Name":"wacom:core#e2eLinkedTo","Icon":null,"DateAdded":"2026-08-31T10:29:44.5894164+00:00",'
        '"DateModified":"0001-01-01T00:00:00","Context":"core","Orphaned":false}}',
        "context": "core",
        "kind": "INSERT_RELATION",
        "tenantId": TENANT_ID,
        "timeStamp": "2026-08-31T10:29:44.613Z",
        "version": 2,
    },
    {
        "body": '{"Data":{"Kind":0,"SubPropertyOf":null,"InverseOf":"wacom:core#e2eLinkedTo",'
        '"Domains":["wacom:core#E2ELifecycleDetail"],"Ranges":["wacom:core#E2ELifecycle"],'
        '"Id":"6a955799cc125f3279246fb0","TenantId":"6a95578d750b9cb0283eddb4",'
        '"Labels":[{"Value":"linked from","Lang":"en"}],"Comments":[],'
        '"Name":"wacom:core#e2eLinkedFrom","Icon":null,"DateAdded":"2026-08-31T10:29:45.0010561+00:00",'
        '"DateModified":"0001-01-01T00:00:00","Context":"core","Orphaned":false}}',
        "context": "core",
        "kind": "INSERT_RELATION",
        "tenantId": TENANT_ID,
        "timeStamp": "2026-08-31T10:29:45.023Z",
        "version": 2,
    },
    {
        "body": '{"ElementUri":"wacom:core#e2eLinkedTo","Data":{"Kind":0,"SubPropertyOf":null,'
        '"InverseOf":"wacom:core#e2eLinkedFrom","Domains":["wacom:core#E2ELifecycle"],'
        '"Ranges":["wacom:core#E2ELifecycleDetail"],"Id":"6a955798cc125f3279246faf",'
        '"TenantId":"6a95578d750b9cb0283eddb4","Labels":[{"Value":"linked to","Lang":"en"}],'
        '"Comments":[{"Value":"Links a lifecycle entity to one of its details.","Lang":"en"}],'
        '"Name":"wacom:core#e2eLinkedTo","Icon":null,"DateAdded":"2026-08-31T10:29:44.589Z",'
        '"DateModified":"2026-08-31T10:29:45.035Z","Context":"core","Orphaned":false}}',
        "context": "core",
        "kind": "CHANGE_RELATION",
        "tenantId": TENANT_ID,
        "timeStamp": "2026-08-31T10:29:45.07Z",
        "version": 2,
    },
]

LIFECYCLE_CLASS: OntologyClassReference = OntologyClassReference.parse("wacom:core#E2ELifecycle")
LIFECYCLE_DETAIL: OntologyClassReference = OntologyClassReference.parse("wacom:core#E2ELifecycleDetail")
CODE_NAME: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#e2eCodeName")
LINKED_TO: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#e2eLinkedTo")
LINKED_FROM: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#e2eLinkedFrom")


# ------------------------------------------- Envelope -----------------------------------------------------------------
def test_pending_version_reports_version_and_change_count() -> None:
    pending = PendingOntologyVersion.from_list(PENDING_PAYLOAD)

    assert pending.version == 2
    assert len(pending.changes) == 7
    assert pending.is_empty is False


def test_pending_version_of_an_empty_list_has_no_version() -> None:
    pending = PendingOntologyVersion.from_list([])

    assert pending.version is None
    assert pending.changes == []
    assert pending.is_empty is True


def test_pending_version_groups_the_changed_elements_by_kind() -> None:
    pending = PendingOntologyVersion.from_list(PENDING_PAYLOAD)

    assert [concept.reference for concept in pending.concepts] == [LIFECYCLE_CLASS, LIFECYCLE_DETAIL]
    assert [prop.reference.property_name for prop in pending.data_properties] == ["e2eCodeName", "e2eRevision"]
    # The relation appears twice: once inserted, once changed.
    assert [prop.reference for prop in pending.object_properties] == [LINKED_TO, LINKED_FROM, LINKED_TO]


# --------------------------------------- Record envelope fields -------------------------------------------------------
def test_record_splits_the_kind_into_operation_and_element_kind() -> None:
    records = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes

    assert records[0].kind == "INSERT_CONCEPT"
    assert records[0].operation is OntologyChangeOperation.INSERT
    assert records[0].element_kind is OntologyElementKind.CONCEPT

    assert records[2].operation is OntologyChangeOperation.INSERT
    assert records[2].element_kind is OntologyElementKind.LITERAL

    assert records[6].operation is OntologyChangeOperation.CHANGE
    assert records[6].element_kind is OntologyElementKind.RELATION


def test_record_carries_the_envelope_metadata() -> None:
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[0]

    assert record.context == "core"
    assert record.tenant_id == TENANT_ID
    assert record.version == 2


def test_record_parses_the_dotnet_timestamp_as_an_aware_datetime() -> None:
    records = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes

    # A 'Z' suffix and three fractional digits.
    assert records[0].time_stamp == datetime(2026, 8, 31, 10, 29, 42, 298000, tzinfo=timezone.utc)
    # Two fractional digits - the service does not pad them.
    assert records[6].time_stamp == datetime(2026, 8, 31, 10, 29, 45, 70000, tzinfo=timezone.utc)


def test_record_keeps_the_decoded_body():
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[0]

    # Nothing from the wire is lost: the PascalCase body stays available verbatim.
    assert record.body["Data"]["Id"] == "6a955796cc125f3279246fa8"
    assert record.body["Data"]["DateAdded"] == "2026-08-31T10:29:42.1946908+00:00"
    assert record.body["Data"]["Orphaned"] is False


# ------------------------------------------ Concept changes -----------------------------------------------------------
def test_insert_concept_record_parses_the_body_into_an_ontology_class() -> None:
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[0]

    concept = record.concept
    assert isinstance(concept, OntologyClass)
    assert concept.reference == LIFECYCLE_CLASS
    assert concept.subclass_of == OntologyClassReference.parse("wacom:core#Thing")
    assert concept.tenant_id == TENANT_ID
    assert concept.context == "core"
    assert concept.icon is None
    assert {label.language_code: label.content for label in concept.labels} == {
        "en": "E2E lifecycle class",
        "de": "E2E-Lebenszyklus-Klasse",
    }
    assert [comment.content for comment in concept.comments] == [
        "Temporary class created by the ontology lifecycle test."
    ]
    assert record.element is concept
    assert record.ontology_property is None


def test_insert_concept_record_exposes_the_element_uri() -> None:
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[1]

    # Insertions carry no ElementUri, so the name of the inserted element is used.
    assert record.element_uri == LIFECYCLE_DETAIL.iri
    assert record.concept.subclass_of == LIFECYCLE_CLASS


# ----------------------------------------- Data-property changes ------------------------------------------------------
def test_insert_literal_record_parses_the_body_into_a_data_property() -> None:
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[2]

    prop = record.ontology_property
    assert isinstance(prop, OntologyProperty)
    assert prop.reference == CODE_NAME
    # 'Kind: 1' on the wire means a literal, i.e. a data property.
    assert prop.kind is PropertyType.DATA_PROPERTY
    assert prop.is_data_property is True
    assert prop.domains == [LIFECYCLE_CLASS]
    assert [entry.iri for entry in prop.ranges] == [DataPropertyType.STRING.value]
    assert prop.subproperty_of is None
    assert prop.inverse_property_of is None
    assert record.concept is None


def test_insert_literal_record_keeps_the_xsd_integer_range() -> None:
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[3]

    assert [entry.iri for entry in record.ontology_property.ranges] == [DataPropertyType.INTEGER.value]


# ---------------------------------------- Object-property changes -----------------------------------------------------
def test_insert_relation_record_parses_the_body_into_an_object_property() -> None:
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[4]

    prop = record.ontology_property
    # 'Kind: 0' on the wire means a relation, i.e. an object property.
    assert prop.kind is PropertyType.OBJECT_PROPERTY
    assert prop.is_data_property is False
    assert prop.reference == LINKED_TO
    assert prop.domains == [LIFECYCLE_CLASS]
    assert prop.ranges == [LIFECYCLE_DETAIL]
    assert prop.inverse_property_of is None


def test_insert_relation_record_parses_the_inverse_property() -> None:
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[5]

    assert record.ontology_property.reference == LINKED_FROM
    assert record.ontology_property.inverse_property_of == LINKED_TO


def test_change_relation_record_takes_its_element_uri_from_the_body() -> None:
    record = PendingOntologyVersion.from_list(PENDING_PAYLOAD).changes[6]

    assert record.operation is OntologyChangeOperation.CHANGE
    assert record.element_uri == LINKED_TO.iri
    # The change is the inverse being wired up on the forward property.
    assert record.ontology_property.inverse_property_of == LINKED_FROM


# --------------------------------------------- Robustness -------------------------------------------------------------
def test_record_tolerates_a_kind_it_does_not_know() -> None:
    record = OntologyChangeRecord.from_dict(
        {
            "body": '{"ElementUri":"wacom:core#E2ELifecycle","Data":null}',
            "context": "core",
            "kind": "RENAME_SOMETHING_NEW",
            "tenantId": TENANT_ID,
            "timeStamp": "2026-08-31T10:29:45.07Z",
            "version": 2,
        }
    )

    # An unrecognised kind must not raise; the raw value stays available.
    assert record.kind == "RENAME_SOMETHING_NEW"
    assert record.operation is None
    assert record.element_kind is None
    assert record.element is None
    assert record.element_uri == "wacom:core#E2ELifecycle"


def test_record_tolerates_a_body_without_a_data_payload() -> None:
    record = OntologyChangeRecord.from_dict(
        {
            "body": '{"ElementUri":"wacom:core#e2eCodeName"}',
            "context": "core",
            "kind": "DELETE_LITERAL",
            "tenantId": TENANT_ID,
            "timeStamp": "2026-08-31T10:29:45.07Z",
            "version": 3,
        }
    )

    assert record.operation is OntologyChangeOperation.DELETE
    assert record.element_kind is OntologyElementKind.LITERAL
    assert record.element is None
    assert record.ontology_property is None
    assert record.element_uri == "wacom:core#e2eCodeName"


def test_record_tolerates_a_missing_body() -> None:
    record = OntologyChangeRecord.from_dict({"context": "core", "kind": "INSERT_CONCEPT", "version": 1})

    assert record.body == {}
    assert record.element is None
    assert record.element_uri is None
    assert record.time_stamp is None
    assert record.tenant_id is None
