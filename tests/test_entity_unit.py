# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
"""Unit tests for knowledge/base/entity.py"""

import pytest

from knowledge.base.entity import (
    # Exceptions
    ServiceException,
    KnowledgeException,
    # Constants
    RDF_SYNTAX_NS_TYPE,
    RDF_SCHEMA_COMMENT,
    RDF_SCHEMA_LABEL,
    ALIAS_TAG,
    DATA_PROPERTY_TAG,
    VALUE_TAG,
    LANGUAGE_TAG,
    LOCALE_TAG,
    DATA_PROPERTIES_TAG,
    SEND_TO_NEL_TAG,
    SEND_VECTOR_INDEX_TAG,
    SOURCE_REFERENCE_ID_TAG,
    EXTERNAL_USER_ID_TAG,
    SOURCE_SYSTEM_TAG,
    OBJECT_PROPERTIES_TAG,
    OWNER_TAG,
    OWNER_ID_TAG,
    GROUP_IDS,
    LOCALIZED_CONTENT_TAG,
    STATUS_FLAG_TAG,
    CONTENT_TAG,
    URI_TAG,
    URIS_TAG,
    FORCE_TAG,
    ERRORS_TAG,
    TEXT_TAG,
    TYPE_TAG,
    IMAGE_TAG,
    DESCRIPTION_TAG,
    COMMENT_TAG,
    COMMENTS_TAG,
    DESCRIPTIONS_TAG,
    REPOSITORY_TAG,
    DISPLAY_TAG,
    USE_NEL_TAG,
    USE_VECTOR_INDEX_TAG,
    USE_VECTOR_DOCUMENT_INDEX_TAG,
    USE_FULLTEXT_TAG,
    TARGETS_TAG,
    VISIBILITY_TAG,
    RELATIONS_TAG,
    INCLUDE_RELATIONS_TAG,
    LABELS_TAG,
    IS_MAIN_TAG,
    DATA_TYPE_TAG,
    RELATION_TAG,
    OUTGOING_TAG,
    INCOMING_TAG,
    TENANT_RIGHTS_TAG,
    INFLECTION_CONCEPT_CLASS,
    INFLECTION_SETTING,
    INFLECTION_CASE_SENSITIVE,
    INDEXING_NEL_TARGET,
    INDEXING_VECTOR_SEARCH_TARGET,
    INDEXING_VECTOR_SEARCH_DOCUMENT_TARGET,
    INDEXING_FULLTEXT_TARGET,
    # Classes
    EntityStatus,
    LocalizedContent,
    Label,
    Description,
)
from knowledge.base.language import LocaleCode, LanguageCode, EN_US, DE_DE


# ================================================================================================
# Exception Tests
# ================================================================================================
class TestServiceException:
    """Tests for ServiceException."""

    def test_service_exception_creation(self):
        """Test ServiceException can be raised and caught."""
        with pytest.raises(ServiceException):
            raise ServiceException("Test service error")

    def test_service_exception_message(self):
        """Test ServiceException preserves message."""
        try:
            raise ServiceException("Custom service error message")
        except ServiceException as e:
            assert str(e) == "Custom service error message"

    def test_service_exception_is_exception(self):
        """Test ServiceException inherits from Exception."""
        assert issubclass(ServiceException, Exception)


class TestKnowledgeException:
    """Tests for KnowledgeException."""

    def test_knowledge_exception_creation(self):
        """Test KnowledgeException can be raised and caught."""
        with pytest.raises(KnowledgeException):
            raise KnowledgeException("Test knowledge error")

    def test_knowledge_exception_message(self):
        """Test KnowledgeException preserves message."""
        try:
            raise KnowledgeException("Custom knowledge error message")
        except KnowledgeException as e:
            assert str(e) == "Custom knowledge error message"

    def test_knowledge_exception_is_exception(self):
        """Test KnowledgeException inherits from Exception."""
        assert issubclass(KnowledgeException, Exception)


# ================================================================================================
# Constants Tests
# ================================================================================================
class TestConstants:
    """Tests for entity constants."""

    def test_rdf_constants(self):
        """Test RDF namespace constants."""
        assert RDF_SYNTAX_NS_TYPE == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        assert RDF_SCHEMA_COMMENT == "http://www.w3.org/2000/01/rdf-schema#comment"
        assert RDF_SCHEMA_LABEL == "http://www.w3.org/2000/01/rdf-schema#label"

    def test_tag_constants(self):
        """Test various tag constants."""
        assert ALIAS_TAG == "alias"
        assert DATA_PROPERTY_TAG == "literal"
        assert VALUE_TAG == "value"
        assert LANGUAGE_TAG == "lang"
        assert LOCALE_TAG == "locale"
        assert DATA_PROPERTIES_TAG == "literals"
        assert SEND_TO_NEL_TAG == "sendToNEL"
        assert SEND_VECTOR_INDEX_TAG == "sendToVectorIndex"

    def test_source_reference_constants(self):
        """Test source reference constants."""
        assert SOURCE_REFERENCE_ID_TAG == "source_reference_id"
        assert EXTERNAL_USER_ID_TAG == "external_user_id"
        assert SOURCE_SYSTEM_TAG == "source_system"

    def test_object_property_constants(self):
        """Test object property constants."""
        assert OBJECT_PROPERTIES_TAG == "relations"
        assert OWNER_TAG == "owner"
        assert OWNER_ID_TAG == "ownerId"
        assert GROUP_IDS == "groupIds"

    def test_content_constants(self):
        """Test content constants."""
        assert LOCALIZED_CONTENT_TAG == "LocalizedContent"
        assert STATUS_FLAG_TAG == "status"
        assert CONTENT_TAG == "value"
        assert URI_TAG == "uri"
        assert URIS_TAG == "uris"
        assert FORCE_TAG == "force"
        assert ERRORS_TAG == "errors"

    def test_text_and_type_constants(self):
        """Test text and type constants."""
        assert TEXT_TAG == "text"
        assert TYPE_TAG == "type"
        assert IMAGE_TAG == "image"
        assert DESCRIPTION_TAG == "description"
        assert COMMENT_TAG == "text"
        assert COMMENTS_TAG == "comments"
        assert DESCRIPTIONS_TAG == "descriptions"

    def test_display_constants(self):
        """Test display constants."""
        assert REPOSITORY_TAG == "repository"
        assert DISPLAY_TAG == "display"

    def test_use_flags_constants(self):
        """Test use flag constants."""
        assert USE_NEL_TAG == "use_for_nel"
        assert USE_VECTOR_INDEX_TAG == "use_for_vector_index"
        assert USE_VECTOR_DOCUMENT_INDEX_TAG == "use_for_vector_document_index"
        assert USE_FULLTEXT_TAG == "user_full_text"

    def test_target_and_visibility_constants(self):
        """Test target and visibility constants."""
        assert TARGETS_TAG == "targets"
        assert VISIBILITY_TAG == "visibility"
        assert RELATIONS_TAG == "relations"
        assert INCLUDE_RELATIONS_TAG == "includeRelations"

    def test_label_constants(self):
        """Test label constants."""
        assert LABELS_TAG == "labels"
        assert IS_MAIN_TAG == "isMain"
        assert DATA_TYPE_TAG == "dataType"

    def test_relation_constants(self):
        """Test relation constants."""
        assert RELATION_TAG == "relation"
        assert OUTGOING_TAG == "out"
        assert INCOMING_TAG == "in"
        assert TENANT_RIGHTS_TAG == "tenantRights"

    def test_inflection_constants(self):
        """Test inflection constants."""
        assert INFLECTION_CONCEPT_CLASS == "concept"
        assert INFLECTION_SETTING == "inflection"
        assert INFLECTION_CASE_SENSITIVE == "caseSensitive"

    def test_indexing_target_constants(self):
        """Test indexing target constants."""
        assert INDEXING_NEL_TARGET == "NEL"
        assert INDEXING_VECTOR_SEARCH_TARGET == "VectorSearchWord"
        assert INDEXING_VECTOR_SEARCH_DOCUMENT_TARGET == "VectorSearchDocument"
        assert INDEXING_FULLTEXT_TARGET == "ElasticSearch"


# ================================================================================================
# EntityStatus Tests
# ================================================================================================
class TestEntityStatus:
    """Tests for EntityStatus enum."""

    def test_entity_status_values(self):
        """Test EntityStatus enum values."""
        assert EntityStatus.UNKNOWN.value == 0
        assert EntityStatus.CREATED.value == 1
        assert EntityStatus.UPDATED.value == 2
        assert EntityStatus.SYNCED.value == 3

    def test_entity_status_names(self):
        """Test EntityStatus enum names."""
        assert EntityStatus.UNKNOWN.name == "UNKNOWN"
        assert EntityStatus.CREATED.name == "CREATED"
        assert EntityStatus.UPDATED.name == "UPDATED"
        assert EntityStatus.SYNCED.name == "SYNCED"

    def test_entity_status_from_value(self):
        """Test creating EntityStatus from value."""
        assert EntityStatus(0) == EntityStatus.UNKNOWN
        assert EntityStatus(1) == EntityStatus.CREATED
        assert EntityStatus(2) == EntityStatus.UPDATED
        assert EntityStatus(3) == EntityStatus.SYNCED

    def test_entity_status_iteration(self):
        """Test iterating over EntityStatus."""
        statuses = list(EntityStatus)
        assert len(statuses) == 4
        assert EntityStatus.UNKNOWN in statuses
        assert EntityStatus.CREATED in statuses
        assert EntityStatus.UPDATED in statuses
        assert EntityStatus.SYNCED in statuses

    def test_entity_status_comparison(self):
        """Test EntityStatus comparison."""
        assert EntityStatus.UNKNOWN != EntityStatus.CREATED
        assert EntityStatus.SYNCED == EntityStatus.SYNCED


# ================================================================================================
# Label Tests
# ================================================================================================
class TestLabel:
    """Tests for Label class."""

    def test_label_creation_basic(self):
        """Test basic Label creation."""
        label = Label("Test Label", EN_US)
        assert label.content == "Test Label"
        assert label.language_code == EN_US
        assert label.main is False

    def test_label_creation_with_main(self):
        """Test Label creation with main flag."""
        label = Label("Main Label", EN_US, main=True)
        assert label.content == "Main Label"
        assert label.language_code == EN_US
        assert label.main is True

    def test_label_creation_default_language(self):
        """Test Label creation with default language."""
        label = Label("Default Lang")
        assert label.content == "Default Lang"
        assert label.language_code == EN_US
        assert label.main is False

    def test_label_creation_different_locale(self):
        """Test Label creation with different locale."""
        label = Label("German Label", DE_DE, main=True)
        assert label.content == "German Label"
        assert label.language_code == DE_DE
        assert label.main is True

    def test_label_content_setter(self):
        """Test Label content setter."""
        label = Label("Original", EN_US)
        label.content = "Modified"
        assert label.content == "Modified"

    def test_label_repr(self):
        """Test Label string representation."""
        label = Label("Test", EN_US)
        assert repr(label) == "Test@en_US"

    def test_label_repr_different_locale(self):
        """Test Label repr with different locale."""
        label = Label("Hallo", DE_DE)
        assert repr(label) == "Hallo@de_DE"

    def test_label_as_dict(self):
        """Test Label as_dict method."""
        label = Label("Test Label", EN_US, main=True)
        result = label.as_dict()
        assert result[CONTENT_TAG] == "Test Label"
        assert result[LOCALE_TAG] == EN_US
        assert result[IS_MAIN_TAG] is True

    def test_label_as_dict_not_main(self):
        """Test Label as_dict when not main."""
        label = Label("Alias Label", EN_US, main=False)
        result = label.as_dict()
        assert result[CONTENT_TAG] == "Alias Label"
        assert result[LOCALE_TAG] == EN_US
        assert result[IS_MAIN_TAG] is False

    def test_label_create_from_dict_basic(self):
        """Test Label.create_from_dict basic usage."""
        data = {
            CONTENT_TAG: "From Dict",
            LOCALE_TAG: "en_US",
        }
        label = Label.create_from_dict(data)
        assert label.content == "From Dict"
        assert label.language_code == LocaleCode("en_US")
        assert label.main is False

    def test_label_create_from_dict_with_main(self):
        """Test Label.create_from_dict with main flag."""
        data = {
            CONTENT_TAG: "Main From Dict",
            LOCALE_TAG: "en_US",
            IS_MAIN_TAG: True,
        }
        label = Label.create_from_dict(data)
        assert label.content == "Main From Dict"
        assert label.language_code == LocaleCode("en_US")
        assert label.main is True

    def test_label_create_from_dict_custom_tags(self):
        """Test Label.create_from_dict with custom tag names."""
        data = {
            "text": "Custom Tag Label",
            "lang": "de_DE",
        }
        label = Label.create_from_dict(data, tag_name="text", locale_name="lang")
        assert label.content == "Custom Tag Label"
        assert label.language_code == LocaleCode("de_DE")

    def test_label_create_from_dict_missing_content(self):
        """Test Label.create_from_dict raises error on missing content."""
        data = {
            LOCALE_TAG: "en_US",
        }
        with pytest.raises(ValueError, match="does not contain a localized label"):
            Label.create_from_dict(data)

    def test_label_create_from_dict_missing_locale(self):
        """Test Label.create_from_dict raises error on missing locale."""
        data = {
            CONTENT_TAG: "Label without locale",
        }
        with pytest.raises(ValueError, match="does not contain a language code"):
            Label.create_from_dict(data)

    def test_label_create_from_list(self):
        """Test Label.create_from_list."""
        data = [
            {CONTENT_TAG: "Label 1", LOCALE_TAG: "en_US", IS_MAIN_TAG: True},
            {CONTENT_TAG: "Label 2", LOCALE_TAG: "de_DE", IS_MAIN_TAG: False},
            {CONTENT_TAG: "Label 3", LOCALE_TAG: "fr_FR"},
        ]
        labels = Label.create_from_list(data)
        assert len(labels) == 3
        assert labels[0].content == "Label 1"
        assert labels[0].main is True
        assert labels[1].content == "Label 2"
        assert labels[1].language_code == LocaleCode("de_DE")
        assert labels[2].content == "Label 3"
        assert labels[2].main is False

    def test_label_create_from_list_empty(self):
        """Test Label.create_from_list with empty list."""
        labels = Label.create_from_list([])
        assert labels == []

    def test_label_round_trip(self):
        """Test Label serialization round trip."""
        original = Label("Round Trip", EN_US, main=True)
        data = original.as_dict()
        # Convert locale back to string for create_from_dict
        data[LOCALE_TAG] = str(data[LOCALE_TAG])
        restored = Label.create_from_dict(data)
        assert restored.content == original.content
        assert restored.main == original.main


# ================================================================================================
# Description Tests
# ================================================================================================
class TestDescription:
    """Tests for Description class."""

    def test_description_creation_basic(self):
        """Test basic Description creation."""
        desc = Description("A test description", EN_US)
        assert desc.content == "A test description"
        assert desc.language_code == EN_US

    def test_description_creation_default_language(self):
        """Test Description creation with default language."""
        desc = Description("Default lang description")
        assert desc.content == "Default lang description"
        assert desc.language_code == EN_US

    def test_description_creation_different_locale(self):
        """Test Description creation with different locale."""
        desc = Description("Eine Beschreibung", DE_DE)
        assert desc.content == "Eine Beschreibung"
        assert desc.language_code == DE_DE

    def test_description_content_setter(self):
        """Test Description content setter."""
        desc = Description("Original description", EN_US)
        desc.content = "Modified description"
        assert desc.content == "Modified description"

    def test_description_repr(self):
        """Test Description string representation."""
        desc = Description("Test description", EN_US)
        assert repr(desc) == "Test description@en_US"

    def test_description_repr_different_locale(self):
        """Test Description repr with different locale."""
        desc = Description("Beschreibung", DE_DE)
        assert repr(desc) == "Beschreibung@de_DE"

    def test_description_as_dict(self):
        """Test Description as_dict method."""
        desc = Description("Dict description", EN_US)
        result = desc.as_dict()
        assert result[DESCRIPTION_TAG] == "Dict description"
        assert result[LOCALE_TAG] == EN_US

    def test_description_create_from_dict_basic(self):
        """Test Description.create_from_dict basic usage."""
        data = {
            DESCRIPTION_TAG: "From Dict",
            LOCALE_TAG: "en_US",
        }
        desc = Description.create_from_dict(data)
        assert desc.content == "From Dict"
        assert desc.language_code == LocaleCode("en_US")

    def test_description_create_from_dict_custom_tags(self):
        """Test Description.create_from_dict with custom tag names."""
        data = {
            "text": "Custom Tag Description",
            "lang": "de_DE",
        }
        desc = Description.create_from_dict(data, tag_name="text", locale_name="lang")
        assert desc.content == "Custom Tag Description"
        assert desc.language_code == LocaleCode("de_DE")

    def test_description_create_from_dict_missing_content(self):
        """Test Description.create_from_dict raises error on missing content."""
        data = {
            LOCALE_TAG: "en_US",
        }
        with pytest.raises(ValueError, match="does not contain a localized label"):
            Description.create_from_dict(data)

    def test_description_create_from_dict_missing_locale(self):
        """Test Description.create_from_dict raises error on missing locale."""
        data = {
            DESCRIPTION_TAG: "Description without locale",
        }
        with pytest.raises(ValueError, match="does not contain a localized label"):
            Description.create_from_dict(data)

    def test_description_create_from_list(self):
        """Test Description.create_from_list."""
        data = [
            {DESCRIPTION_TAG: "Description 1", LOCALE_TAG: "en_US"},
            {DESCRIPTION_TAG: "Description 2", LOCALE_TAG: "de_DE"},
            {DESCRIPTION_TAG: "Description 3", LOCALE_TAG: "fr_FR"},
        ]
        descriptions = Description.create_from_list(data)
        assert len(descriptions) == 3
        assert descriptions[0].content == "Description 1"
        assert descriptions[1].content == "Description 2"
        assert descriptions[1].language_code == LocaleCode("de_DE")
        assert descriptions[2].content == "Description 3"

    def test_description_create_from_list_empty(self):
        """Test Description.create_from_list with empty list."""
        descriptions = Description.create_from_list([])
        assert descriptions == []

    def test_description_round_trip(self):
        """Test Description serialization round trip."""
        original = Description("Round Trip Description", EN_US)
        data = original.as_dict()
        # Convert locale back to string for create_from_dict
        data[LOCALE_TAG] = str(data[LOCALE_TAG])
        restored = Description.create_from_dict(data)
        assert restored.content == original.content


# ================================================================================================
# LocalizedContent Tests (via Label and Description)
# ================================================================================================
class TestLocalizedContent:
    """Tests for LocalizedContent abstract base class via its subclasses."""

    def test_localized_content_inheritance_label(self):
        """Test Label inherits from LocalizedContent."""
        assert issubclass(Label, LocalizedContent)

    def test_localized_content_inheritance_description(self):
        """Test Description inherits from LocalizedContent."""
        assert issubclass(Description, LocalizedContent)

    def test_localized_content_properties_via_label(self):
        """Test LocalizedContent properties via Label."""
        label = Label("Test Content", EN_US)
        assert hasattr(label, "content")
        assert hasattr(label, "language_code")
        assert label.content == "Test Content"
        assert label.language_code == EN_US

    def test_localized_content_properties_via_description(self):
        """Test LocalizedContent properties via Description."""
        desc = Description("Test Description", DE_DE)
        assert hasattr(desc, "content")
        assert hasattr(desc, "language_code")
        assert desc.content == "Test Description"
        assert desc.language_code == DE_DE

    def test_localized_content_setter_via_label(self):
        """Test LocalizedContent content setter via Label."""
        label = Label("Original", EN_US)
        label.content = "Updated"
        assert label.content == "Updated"

    def test_localized_content_repr_format(self):
        """Test LocalizedContent repr format is consistent."""
        label = Label("LabelText", EN_US)
        desc = Description("DescText", EN_US)
        # Both should follow same format: content@language_code
        assert "@" in repr(label)
        assert "@" in repr(desc)
        assert repr(label).startswith("LabelText@")
        assert repr(desc).startswith("DescText@")

    def test_localized_content_with_language_code(self):
        """Test LocalizedContent with LanguageCode type."""
        # Labels can accept LanguageCode as well as LocaleCode
        label = Label("Test", LanguageCode("en"))
        assert label.language_code == LanguageCode("en")
        assert repr(label) == "Test@en"


# ================================================================================================
# Edge Cases and Error Handling Tests
# ================================================================================================
class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_label_empty_content(self):
        """Test Label with empty content."""
        label = Label("", EN_US)
        assert label.content == ""
        assert repr(label) == "@en_US"

    def test_description_empty_content(self):
        """Test Description with empty content."""
        desc = Description("", EN_US)
        assert desc.content == ""
        assert repr(desc) == "@en_US"

    def test_label_unicode_content(self):
        """Test Label with unicode content."""
        label = Label("日本語テスト", LocaleCode("ja_JP"))
        assert label.content == "日本語テスト"
        assert "日本語テスト" in repr(label)

    def test_description_unicode_content(self):
        """Test Description with unicode content."""
        desc = Description("Ελληνικά", LocaleCode("el_GR"))
        assert desc.content == "Ελληνικά"
        assert "Ελληνικά" in repr(desc)

    def test_label_special_characters(self):
        """Test Label with special characters."""
        label = Label("Test & <script>alert('xss')</script>", EN_US)
        assert label.content == "Test & <script>alert('xss')</script>"

    def test_label_multiline_content(self):
        """Test Label with multiline content."""
        label = Label("Line 1\nLine 2\nLine 3", EN_US)
        assert "Line 1" in label.content
        assert "\n" in label.content

    def test_description_long_content(self):
        """Test Description with long content."""
        long_text = "A" * 10000
        desc = Description(long_text, EN_US)
        assert len(desc.content) == 10000
        assert desc.content == long_text

    def test_label_create_from_dict_extra_fields(self):
        """Test Label.create_from_dict ignores extra fields."""
        data = {
            CONTENT_TAG: "Label",
            LOCALE_TAG: "en_US",
            IS_MAIN_TAG: True,
            "extra_field": "ignored",
            "another_field": 123,
        }
        label = Label.create_from_dict(data)
        assert label.content == "Label"
        assert label.main is True

    def test_description_create_from_dict_extra_fields(self):
        """Test Description.create_from_dict ignores extra fields."""
        data = {
            DESCRIPTION_TAG: "Description",
            LOCALE_TAG: "en_US",
            "extra_field": "ignored",
        }
        desc = Description.create_from_dict(data)
        assert desc.content == "Description"

    def test_multiple_labels_same_locale(self):
        """Test multiple labels with same locale."""
        labels = [
            Label("Main Label", EN_US, main=True),
            Label("Alias 1", EN_US, main=False),
            Label("Alias 2", EN_US, main=False),
        ]
        main_labels = [lbl for lbl in labels if lbl.main]
        alias_labels = [lbl for lbl in labels if not lbl.main]
        assert len(main_labels) == 1
        assert len(alias_labels) == 2

    def test_label_is_main_false_by_default(self):
        """Test that is_main defaults to False in create_from_dict."""
        data = {
            CONTENT_TAG: "No main flag",
            LOCALE_TAG: "en_US",
        }
        label = Label.create_from_dict(data)
        assert label.main is False
