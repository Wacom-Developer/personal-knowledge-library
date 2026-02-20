# -*- coding: utf-8 -*-
# Copyright © 2025-present Wacom. All rights reserved.
"""
Unit tests for knowledge/base/ontology.py

These tests verify the ontology data structures and parsing logic
without requiring network access.
"""

import json
import pytest

from knowledge.base.entity import (
    Label,
    Description,
    CONTENT_TAG,
    LOCALE_TAG,
    DATA_PROPERTY_TAG,
    DATA_TYPE_TAG,
    RELATION_TAG,
    INCOMING_TAG,
    OUTGOING_TAG,
)
from knowledge.base.language import EN_US, LocaleCode
from knowledge.base.ontology import (
    # Enums
    PropertyType,
    DataPropertyType,
    INVERSE_DATA_PROPERTY_TYPE_MAPPING,
    # References
    OntologyClassReference,
    OntologyPropertyReference,
    # Properties
    DataProperty,
    ObjectProperty,
    # Entity
    ThingObject,
    THING_CLASS,
    # Settings
    InflectionSetting,
    # Encoder
    ThingEncoder,
    # Labels
    OntologyLabel,
    # Constants
    SYSTEM_SOURCE_REFERENCE_ID,
    SYSTEM_SOURCE_SYSTEM,
)


class TestPropertyType:
    """Tests for PropertyType enum."""

    def test_property_type_values(self):
        """Test that PropertyType has expected values."""
        assert PropertyType.OBJECT_PROPERTY.value == "Relation"
        assert PropertyType.DATA_PROPERTY.value == "Literal"

    def test_property_type_members(self):
        """Test that PropertyType has exactly two members."""
        assert len(PropertyType) == 2


class TestDataPropertyType:
    """Tests for DataPropertyType enum."""

    def test_string_type(self):
        """Test STRING data type."""
        assert DataPropertyType.STRING.value == "http://www.w3.org/2001/XMLSchema#string"

    def test_boolean_type(self):
        """Test BOOLEAN data type."""
        assert DataPropertyType.BOOLEAN.value == "http://www.w3.org/2001/XMLSchema#boolean"

    def test_integer_type(self):
        """Test INTEGER data type."""
        assert DataPropertyType.INTEGER.value == "http://www.w3.org/2001/XMLSchema#integer"

    def test_datetime_type(self):
        """Test DATE_TIME data type."""
        assert DataPropertyType.DATE_TIME.value == "http://www.w3.org/2001/XMLSchema#dateTime"

    def test_inverse_mapping(self):
        """Test that inverse mapping works correctly."""
        for dtype in DataPropertyType:
            assert INVERSE_DATA_PROPERTY_TYPE_MAPPING[str(dtype.value)] == dtype


class TestOntologyClassReference:
    """Tests for OntologyClassReference class."""

    def test_create_from_components(self):
        """Test creating reference from scheme, context, and name."""
        ref = OntologyClassReference("wacom", "core", "Person")
        assert ref.scheme == "wacom"
        assert ref.context == "core"
        assert ref.name == "Person"
        assert ref.class_name == "Person"
        assert ref.iri == "wacom:core#Person"

    def test_parse_valid_iri(self):
        """Test parsing a valid IRI."""
        ref = OntologyClassReference.parse("wacom:core#Thing")
        assert ref.scheme == "wacom"
        assert ref.context == "core"
        assert ref.name == "Thing"
        assert ref.iri == "wacom:core#Thing"

    def test_parse_invalid_iri_no_colon(self):
        """Test that parsing an IRI without colon raises ValueError."""
        with pytest.raises(ValueError, match="Invalid IRI"):
            OntologyClassReference.parse("invalidiri")

    def test_parse_invalid_iri_no_hash(self):
        """Test that parsing an IRI without hash raises ValueError."""
        with pytest.raises(ValueError, match="Invalid IRI"):
            OntologyClassReference.parse("wacom:core")

    def test_parse_none_iri(self):
        """Test that parsing None raises ValueError."""
        with pytest.raises(ValueError, match="IRI cannot be None"):
            OntologyClassReference.parse(None)

    def test_equality(self):
        """Test equality comparison."""
        ref1 = OntologyClassReference("wacom", "core", "Person")
        ref2 = OntologyClassReference("wacom", "core", "Person")
        ref3 = OntologyClassReference("wacom", "core", "Organization")

        assert ref1 == ref2
        assert ref1 != ref3

    def test_hash(self):
        """Test that references with same IRI have same hash."""
        ref1 = OntologyClassReference("wacom", "core", "Person")
        ref2 = OntologyClassReference("wacom", "core", "Person")

        assert hash(ref1) == hash(ref2)

    def test_repr(self):
        """Test string representation."""
        ref = OntologyClassReference("wacom", "core", "Person")
        assert repr(ref) == "wacom:core#Person"


class TestOntologyPropertyReference:
    """Tests for OntologyPropertyReference class."""

    def test_create_from_components(self):
        """Test creating reference from scheme, context, and property name."""
        ref = OntologyPropertyReference("wacom", "core", "hasAuthor")
        assert ref.scheme == "wacom"
        assert ref.context == "core"
        assert ref.name == "hasAuthor"
        assert ref.property_name == "hasAuthor"
        assert ref.iri == "wacom:core#hasAuthor"

    def test_parse_valid_iri(self):
        """Test parsing a valid property IRI."""
        ref = OntologyPropertyReference.parse("wacom:core#sourceSystem")
        assert ref.scheme == "wacom"
        assert ref.context == "core"
        assert ref.property_name == "sourceSystem"

    def test_equality(self):
        """Test equality comparison for property references."""
        ref1 = OntologyPropertyReference("wacom", "core", "prop1")
        ref2 = OntologyPropertyReference("wacom", "core", "prop1")
        ref3 = OntologyPropertyReference("wacom", "core", "prop2")

        assert ref1 == ref2
        assert ref1 != ref3

    def test_hash(self):
        """Test that property references with same IRI have same hash."""
        ref1 = OntologyPropertyReference("wacom", "core", "prop")
        ref2 = OntologyPropertyReference("wacom", "core", "prop")

        assert hash(ref1) == hash(ref2)


class TestDataProperty:
    """Tests for DataProperty class."""

    def test_create_basic_data_property(self):
        """Test creating a basic data property."""
        prop_ref = OntologyPropertyReference.parse("wacom:core#customProp")
        dp = DataProperty("test value", prop_ref)

        assert dp.value == "test value"
        assert dp.data_property_type == prop_ref
        assert dp.language_code == EN_US  # default
        assert dp.data_type is None

    def test_create_data_property_with_language(self):
        """Test creating a data property with custom language."""
        prop_ref = OntologyPropertyReference.parse("wacom:core#customProp")
        lang = LocaleCode("de_DE")
        dp = DataProperty("Wert", prop_ref, language_code=lang)

        assert dp.value == "Wert"
        assert dp.language_code == lang

    def test_create_data_property_with_data_type(self):
        """Test creating a data property with explicit data type."""
        prop_ref = OntologyPropertyReference.parse("wacom:core#age")
        dp = DataProperty(25, prop_ref, data_type=DataPropertyType.INTEGER)

        assert dp.value == 25
        assert dp.data_type == DataPropertyType.INTEGER

    def test_as_dict(self):
        """Test converting data property to dictionary."""
        prop_ref = OntologyPropertyReference.parse("wacom:core#customProp")
        dp = DataProperty("value", prop_ref, data_type=DataPropertyType.STRING)

        result = dp.as_dict()

        assert result[CONTENT_TAG] == "value"
        assert result[LOCALE_TAG] == EN_US
        assert result[DATA_PROPERTY_TAG] == "wacom:core#customProp"
        assert result[DATA_TYPE_TAG] == DataPropertyType.STRING.value

    def test_as_dict_no_data_type(self):
        """Test as_dict with no data type returns None for data type."""
        prop_ref = OntologyPropertyReference.parse("wacom:core#prop")
        dp = DataProperty("value", prop_ref)

        result = dp.as_dict()
        assert result[DATA_TYPE_TAG] is None

    def test_create_from_dict(self):
        """Test creating data property from dictionary."""
        data = {
            CONTENT_TAG: "test value",
            LOCALE_TAG: "en_US",
            DATA_PROPERTY_TAG: "wacom:core#testProp",
            DATA_TYPE_TAG: "http://www.w3.org/2001/XMLSchema#string",
        }

        dp = DataProperty.create_from_dict(data)

        assert dp.value == "test value"
        assert dp.data_property_type.iri == "wacom:core#testProp"
        assert dp.data_type == DataPropertyType.STRING

    def test_create_from_dict_invalid(self):
        """Test that creating from invalid dict raises ValueError."""
        with pytest.raises(ValueError):
            DataProperty.create_from_dict({})

    def test_create_from_list(self):
        """Test creating multiple data properties from list."""
        data_list = [
            {
                CONTENT_TAG: "value1",
                LOCALE_TAG: "en_US",
                DATA_PROPERTY_TAG: "wacom:core#prop1",
            },
            {
                CONTENT_TAG: "value2",
                LOCALE_TAG: "de_DE",
                DATA_PROPERTY_TAG: "wacom:core#prop2",
            },
        ]

        properties = DataProperty.create_from_list(data_list)

        assert len(properties) == 2
        assert properties[0].value == "value1"
        assert properties[1].value == "value2"

    def test_repr(self):
        """Test string representation of data property."""
        prop_ref = OntologyPropertyReference.parse("wacom:core#myProp")
        dp = DataProperty("value", prop_ref)

        assert "value" in repr(dp)
        assert "myProp" in repr(dp)


class TestObjectProperty:
    """Tests for ObjectProperty class."""

    def test_create_empty_object_property(self):
        """Test creating an empty object property."""
        rel_ref = OntologyPropertyReference.parse("wacom:core#relatedTo")
        op = ObjectProperty(relation=rel_ref)

        assert op.relation == rel_ref
        assert op.incoming_relations == []
        assert op.outgoing_relations == []

    def test_create_with_incoming_relations(self):
        """Test creating object property with incoming relations."""
        rel_ref = OntologyPropertyReference.parse("wacom:core#relatedTo")
        op = ObjectProperty(relation=rel_ref, incoming=["wacom:entity:1", "wacom:entity:2"])

        assert len(op.incoming_relations) == 2
        assert "wacom:entity:1" in op.incoming_relations
        assert "wacom:entity:2" in op.incoming_relations

    def test_create_with_outgoing_relations(self):
        """Test creating object property with outgoing relations."""
        rel_ref = OntologyPropertyReference.parse("wacom:core#relatedTo")
        op = ObjectProperty(relation=rel_ref, outgoing=["wacom:entity:3", "wacom:entity:4"])

        assert len(op.outgoing_relations) == 2
        assert "wacom:entity:3" in op.outgoing_relations

    def test_as_dict_with_string_relations(self):
        """Test converting object property with string relations to dict."""
        rel_ref = OntologyPropertyReference.parse("wacom:core#relatedTo")
        op = ObjectProperty(
            relation=rel_ref,
            incoming=["wacom:entity:in"],
            outgoing=["wacom:entity:out"],
        )

        result = op.as_dict()

        assert result[RELATION_TAG] == "wacom:core#relatedTo"
        assert result[INCOMING_TAG] == ["wacom:entity:in"]
        assert result[OUTGOING_TAG] == ["wacom:entity:out"]

    def test_as_dict_with_thing_objects(self):
        """Test converting object property with ThingObject relations to dict."""
        rel_ref = OntologyPropertyReference.parse("wacom:core#relatedTo")

        # Create ThingObjects
        thing1 = ThingObject(uri="wacom:entity:thing1")
        thing2 = ThingObject()
        thing2.reference_id = "ref-id-2"

        op = ObjectProperty(relation=rel_ref, incoming=[thing1], outgoing=[thing2])

        result = op.as_dict()

        assert result[INCOMING_TAG] == ["wacom:entity:thing1"]
        assert result[OUTGOING_TAG] == ["ref-id-2"]

    def test_create_from_dict(self):
        """Test creating object property from dictionary."""
        data = {
            RELATION_TAG: "wacom:core#relatedTo",
            INCOMING_TAG: ["wacom:entity:in1"],
            OUTGOING_TAG: ["wacom:entity:out1"],
        }

        rel_ref, op = ObjectProperty.create_from_dict(data)

        assert rel_ref.iri == "wacom:core#relatedTo"
        assert op.incoming_relations == ["wacom:entity:in1"]
        assert op.outgoing_relations == ["wacom:entity:out1"]

    def test_create_from_list(self):
        """Test creating object properties from list."""
        data_list = [
            {
                RELATION_TAG: "wacom:core#rel1",
                INCOMING_TAG: [],
                OUTGOING_TAG: ["wacom:entity:1"],
            },
            {
                RELATION_TAG: "wacom:core#rel2",
                INCOMING_TAG: ["wacom:entity:2"],
                OUTGOING_TAG: [],
            },
        ]

        properties = ObjectProperty.create_from_list(data_list)

        assert len(properties) == 2
        ref1 = OntologyPropertyReference.parse("wacom:core#rel1")
        ref2 = OntologyPropertyReference.parse("wacom:core#rel2")
        assert ref1 in properties
        assert ref2 in properties

    def test_repr(self):
        """Test string representation of object property."""
        rel_ref = OntologyPropertyReference.parse("wacom:core#rel")
        op = ObjectProperty(relation=rel_ref, incoming=["in"], outgoing=["out"])

        result = repr(op)

        assert "wacom:core#rel" in result
        assert "in" in result
        assert "out" in result


class TestThingObject:
    """Tests for ThingObject class."""

    def test_create_minimal_thing(self):
        """Test creating a minimal ThingObject."""
        thing = ThingObject()

        assert thing.uri is None
        assert thing.label == []
        assert thing.description == []
        assert thing.concept_type == THING_CLASS
        assert thing.use_for_nel is True  # default
        assert thing.use_vector_index is False  # default

    def test_create_with_uri_and_label(self):
        """Test creating ThingObject with URI and label."""
        label = Label("Test Entity", EN_US, main=True)
        thing = ThingObject(uri="wacom:entity:test", label=[label])

        assert thing.uri == "wacom:entity:test"
        assert len(thing.label) == 1
        assert thing.label[0].content == "Test Entity"

    def test_add_label(self):
        """Test adding a label to ThingObject."""
        thing = ThingObject()
        thing.add_label("My Label", EN_US)

        assert len(thing.label) == 1
        assert thing.label[0].content == "My Label"
        assert thing.label[0].language_code == EN_US

    def test_update_label(self):
        """Test updating an existing label."""
        thing = ThingObject(label=[Label("Original", EN_US, main=True)])
        thing.update_label("Updated", EN_US)

        assert len(thing.label) == 1
        assert thing.label[0].content == "Updated"

    def test_update_label_creates_new_if_not_exists(self):
        """Test that update_label creates a new label if language doesn't exist."""
        thing = ThingObject(label=[Label("English", EN_US, main=True)])
        thing.update_label("German", LocaleCode("de_DE"))

        assert len(thing.label) == 2

    def test_remove_label(self):
        """Test removing a label."""
        thing = ThingObject(
            label=[
                Label("English", EN_US, main=True),
                Label("German", LocaleCode("de_DE")),
            ]
        )
        thing.remove_label(EN_US)

        assert len(thing.label) == 1
        assert thing.label[0].content == "German"

    def test_label_lang(self):
        """Test getting label by language."""
        thing = ThingObject(
            label=[
                Label("English", EN_US, main=True),
                Label("German", LocaleCode("de_DE")),
            ]
        )

        en_label = thing.label_lang(EN_US)
        assert en_label is not None
        assert en_label.content == "English"

        de_label = thing.label_lang(LocaleCode("de_DE"))
        assert de_label is not None
        assert de_label.content == "German"

        fr_label = thing.label_lang(LocaleCode("fr_FR"))
        assert fr_label is None

    def test_add_description(self):
        """Test adding a description."""
        thing = ThingObject()
        thing.add_description("A test entity", EN_US)

        assert len(thing.description) == 1
        assert thing.description[0].content == "A test entity"

    def test_update_description(self):
        """Test updating an existing description."""
        thing = ThingObject(description=[Description("Original", EN_US)])
        thing.update_description("Updated", EN_US)

        assert len(thing.description) == 1
        assert thing.description[0].content == "Updated"

    def test_description_lang(self):
        """Test getting description by language."""
        thing = ThingObject(
            description=[
                Description("English desc", EN_US),
                Description("German desc", LocaleCode("de_DE")),
            ]
        )

        en_desc = thing.description_lang(EN_US)
        assert en_desc is not None
        assert en_desc.content == "English desc"

        none_desc = thing.description_lang(LocaleCode("fr_FR"))
        assert none_desc is None

    def test_remove_description(self):
        """Test removing a description."""
        thing = ThingObject(
            description=[
                Description("Desc 1", EN_US),
                Description("Desc 2", LocaleCode("de_DE")),
            ]
        )
        thing.remove_description(EN_US)

        assert len(thing.description) == 1

    def test_alias_operations(self):
        """Test alias add, update, and remove operations."""
        thing = ThingObject()
        thing.alias = [Label("Alias1", EN_US)]

        # Test alias_lang
        aliases = thing.alias_lang(EN_US)
        assert len(aliases) == 1
        assert aliases[0].content == "Alias1"

        # Test remove_alias
        thing.remove_alias(Label("Alias1", EN_US))
        assert len(thing.alias) == 0

    def test_reference_id_property(self):
        """Test setting and getting reference_id."""
        thing = ThingObject()
        thing.reference_id = "my-ref-id"

        assert thing.reference_id == "my-ref-id"
        assert SYSTEM_SOURCE_REFERENCE_ID in thing.data_properties

    def test_source_system_property(self):
        """Test setting and getting source_system."""
        thing = ThingObject()
        thing.source_system = "my-system"

        assert thing.source_system == "my-system"
        assert SYSTEM_SOURCE_SYSTEM in thing.data_properties

    def test_data_properties(self):
        """Test data properties management."""
        thing = ThingObject()
        prop_ref = OntologyPropertyReference.parse("wacom:core#customProp")

        thing.data_properties[prop_ref] = [DataProperty("value", prop_ref)]

        assert prop_ref in thing.data_properties
        assert thing.data_properties[prop_ref][0].value == "value"

    def test_remove_data_property(self):
        """Test removing a data property."""
        thing = ThingObject()
        prop_ref = OntologyPropertyReference.parse("wacom:core#customProp")
        thing.data_properties[prop_ref] = [DataProperty("value", prop_ref)]

        thing.remove_data_property(prop_ref)

        assert prop_ref not in thing.data_properties

    def test_data_property_lang(self):
        """Test getting data properties by language."""
        thing = ThingObject()
        prop_ref = OntologyPropertyReference.parse("wacom:core#prop")
        thing.data_properties[prop_ref] = [
            DataProperty("english", prop_ref, EN_US),
            DataProperty("german", prop_ref, LocaleCode("de_DE")),
        ]

        en_props = thing.data_property_lang(prop_ref, EN_US)
        assert len(en_props) == 1
        assert en_props[0].value == "english"

    def test_object_properties(self):
        """Test object properties management."""
        thing = ThingObject()
        rel_ref = OntologyPropertyReference.parse("wacom:core#relatedTo")
        obj_prop = ObjectProperty(relation=rel_ref, outgoing=["wacom:entity:other"])

        thing.object_properties[rel_ref] = obj_prop

        assert rel_ref in thing.object_properties
        assert len(thing.object_properties[rel_ref].outgoing_relations) == 1

    def test_visibility(self):
        """Test visibility property."""
        thing = ThingObject()
        assert thing.visibility is None

        thing.visibility = "public"
        assert thing.visibility == "public"

    def test_owner_properties(self):
        """Test owner-related properties."""
        thing = ThingObject(owner=True)
        assert thing.owner is True

        thing.owner_id = "owner-123"
        assert thing.owner_id == "owner-123"

        thing.owner_external_user_id = "ext-user-456"
        assert thing.owner_external_user_id == "ext-user-456"

    def test_group_ids(self):
        """Test group_ids property."""
        thing = ThingObject()
        assert thing.group_ids == []

        thing.group_ids = ["group1", "group2"]
        assert len(thing.group_ids) == 2

        thing.group_ids = None
        assert thing.group_ids == []

    def test_image_property(self):
        """Test image property."""
        thing = ThingObject()
        assert thing.image is None

        thing.image = "https://example.com/image.png"
        assert thing.image == "https://example.com/image.png"

        thing.image = None
        assert thing.image is None


class TestInflectionSetting:
    """Tests for InflectionSetting class."""

    def test_create_inflection_setting(self):
        """Test creating an inflection setting."""
        setting = InflectionSetting(concept="wacom:core#Person", inflection="singular", case_sensitive=True)

        assert setting.concept.iri == "wacom:core#Person"
        assert setting.inflection == "singular"
        assert setting.case_sensitive is True

    def test_from_dict(self):
        """Test creating inflection setting from dictionary."""
        data = {
            "concept": "wacom:core#Organization",
            "inflection": "plural",
            "caseSensitive": False,
        }

        setting = InflectionSetting.from_dict(data)

        assert setting.concept.iri == "wacom:core#Organization"
        assert setting.inflection == "plural"
        assert setting.case_sensitive is False

    def test_from_dict_with_defaults(self):
        """Test from_dict with missing keys uses defaults."""
        data = {}

        # This will create with empty concept which may fail to parse
        # Let's use minimal valid data
        data = {"concept": "wacom:core#Thing"}
        setting = InflectionSetting.from_dict(data)

        assert setting.inflection == ""
        assert setting.case_sensitive is False


class TestOntologyLabel:
    """Tests for OntologyLabel class."""

    def test_create_ontology_label(self):
        """Test creating an ontology label."""
        label = OntologyLabel("Test Label", EN_US)

        assert label.content == "Test Label"
        assert label.language_code == EN_US

    def test_repr(self):
        """Test string representation."""
        label = OntologyLabel("Test", EN_US)
        result = repr(label)

        assert "Test" in result
        assert "en_US" in result


class TestThingEncoder:
    """Tests for ThingEncoder JSON encoder."""

    def test_encode_thing_object(self):
        """Test encoding a ThingObject to JSON."""
        thing = ThingObject(uri="wacom:entity:test", label=[Label("Test", EN_US, main=True)])

        # ThingEncoder should handle ThingObject
        result = json.dumps(thing, cls=ThingEncoder)
        assert "wacom:entity:test" in result
        assert "Test" in result

    def test_encode_label(self):
        """Test encoding a Label to JSON."""
        label = Label("My Label", EN_US, main=True)

        result = json.dumps(label, cls=ThingEncoder)
        assert "My Label" in result

    def test_encode_description(self):
        """Test encoding a Description to JSON."""
        desc = Description("A description", EN_US)

        result = json.dumps(desc, cls=ThingEncoder)
        assert "A description" in result

    def test_encode_regular_types(self):
        """Test that regular types are encoded normally."""
        data = {"key": "value", "number": 42}

        result = json.dumps(data, cls=ThingEncoder)
        parsed = json.loads(result)

        assert parsed["key"] == "value"
        assert parsed["number"] == 42
