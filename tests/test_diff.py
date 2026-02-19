# -*- coding: utf-8 -*-
# Copyright © 2025-present Wacom. All rights reserved.
"""
Unit tests for knowledge/utils/diff.py

These tests verify the entity comparison functionality without requiring
network access by mocking the WacomKnowledgeService client.
"""

import pytest
from typing import List
from unittest.mock import MagicMock, AsyncMock

from knowledge.base.entity import Label, Description
from knowledge.base.language import EN_US, LocaleCode
from knowledge.base.ontology import (
    ThingObject,
    OntologyClassReference,
    OntologyPropertyReference,
    DataProperty,
    ObjectProperty,
    THING_CLASS,
)
from knowledge.utils.diff import (
    diff_entities,
    diff_entities_async,
    is_different,
    is_different_async,
)


class TestDiffEntities:
    """Tests for the diff_entities function."""

    def _create_thing(
        self,
        uri: str = "wacom:entity:test",
        labels: List[Label] = None,
        descriptions: List[Description] = None,
        aliases: List[Label] = None,
        use_for_nel: bool = True,
        use_vector_index: bool = False,
        concept_type: OntologyClassReference = THING_CLASS,
    ) -> ThingObject:
        """Helper to create a ThingObject for testing."""
        thing = ThingObject(
            uri=uri,
            label=labels or [Label("Test Entity", EN_US, main=True)],
            description=descriptions or [],
            concept_type=concept_type,
            use_for_nel=use_for_nel,
            use_vector_index=use_vector_index,
        )
        if aliases:
            thing.alias = aliases
        # Set a source reference id for the entity
        thing.reference_id = "test-ref-id"
        return thing

    def test_identical_entities_no_differences(self):
        """Test that identical entities produce no differences."""
        mock_client = MagicMock()

        file_thing = self._create_thing(
            labels=[Label("Test", EN_US, main=True)],
            descriptions=[Description("A test entity", EN_US)],
        )
        kg_thing = self._create_thing(
            labels=[Label("Test", EN_US, main=True)],
            descriptions=[Description("A test entity", EN_US)],
        )

        differences, data_prop_diff, obj_prop_diff = diff_entities(
            mock_client, file_thing, kg_thing
        )

        assert len(differences) == 0
        assert len(data_prop_diff) == 0
        assert len(obj_prop_diff) == 0

    def test_different_description_count(self):
        """Test detection of different number of descriptions."""
        mock_client = MagicMock()

        file_thing = self._create_thing(
            descriptions=[
                Description("Description 1", EN_US),
                Description("Description 2", LocaleCode("de_DE")),
            ]
        )
        kg_thing = self._create_thing(
            descriptions=[Description("Description 1", EN_US)]
        )

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        # Should detect description count difference
        desc_diffs = [d for d in differences if d["type"] == "description"]
        assert len(desc_diffs) == 1
        assert desc_diffs[0]["kg"] == 2  # file_thing has 2 descriptions
        assert desc_diffs[0]["file"] == 1  # kg_thing has 1 description

    def test_different_description_content(self):
        """Test detection of different description content."""
        mock_client = MagicMock()

        file_thing = self._create_thing(
            descriptions=[Description("Original description", EN_US)]
        )
        kg_thing = self._create_thing(
            descriptions=[Description("Different description", EN_US)]
        )

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        content_diffs = [d for d in differences if d["type"] == "Description content"]
        assert len(content_diffs) == 1
        assert content_diffs[0]["file"] == "Original description"
        assert content_diffs[0]["kg"] == "Different description"

    def test_missing_description(self):
        """Test detection of missing description for a language."""
        mock_client = MagicMock()

        file_thing = self._create_thing(
            descriptions=[Description("German description", LocaleCode("de_DE"))]
        )
        kg_thing = self._create_thing(descriptions=[])

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        missing_diffs = [d for d in differences if d["type"] == "Missing description"]
        assert len(missing_diffs) == 1
        assert missing_diffs[0]["file"] == "German description"

    def test_different_vector_index_flag(self):
        """Test detection of different vector index settings."""
        mock_client = MagicMock()

        file_thing = self._create_thing(use_vector_index=True)
        kg_thing = self._create_thing(use_vector_index=False)

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        vector_diffs = [d for d in differences if d["type"] == "Vector index"]
        assert len(vector_diffs) == 1
        assert vector_diffs[0]["file"] is True
        assert vector_diffs[0]["kg"] is False

    def test_different_nel_flag(self):
        """Test detection of different NEL index settings."""
        mock_client = MagicMock()

        file_thing = self._create_thing(use_for_nel=False)
        kg_thing = self._create_thing(use_for_nel=True)

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        nel_diffs = [d for d in differences if d["type"] == "NEL index"]
        assert len(nel_diffs) == 1
        assert nel_diffs[0]["file"] is False
        assert nel_diffs[0]["kg"] is True

    def test_different_label_count(self):
        """Test detection of different number of labels."""
        mock_client = MagicMock()

        file_thing = self._create_thing(
            labels=[
                Label("English", EN_US, main=True),
                Label("German", LocaleCode("de_DE"), main=False),
            ]
        )
        kg_thing = self._create_thing(labels=[Label("English", EN_US, main=True)])

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        label_diffs = [d for d in differences if d["type"] == "Number of labels"]
        assert len(label_diffs) == 1
        assert label_diffs[0]["file"] == 2
        assert label_diffs[0]["kg"] == 1

    def test_different_label_content(self):
        """Test detection of different label content."""
        mock_client = MagicMock()

        file_thing = self._create_thing(
            labels=[Label("Original Name", EN_US, main=True)]
        )
        kg_thing = self._create_thing(
            labels=[Label("Different Name", EN_US, main=True)]
        )

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        content_diffs = [d for d in differences if d["type"] == "Label content"]
        assert len(content_diffs) == 1

    def test_missing_label(self):
        """Test detection of missing label for a language."""
        mock_client = MagicMock()

        file_thing = self._create_thing(
            labels=[Label("German Label", LocaleCode("de_DE"), main=True)]
        )
        kg_thing = self._create_thing(labels=[Label("English Label", EN_US, main=True)])

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        missing_diffs = [d for d in differences if d["type"] == "Missing label"]
        assert len(missing_diffs) == 1

    def test_different_alias_count(self):
        """Test detection of different number of aliases."""
        mock_client = MagicMock()

        file_thing = self._create_thing()
        file_thing.alias = [
            Label("Alias 1", EN_US),
            Label("Alias 2", EN_US),
        ]

        kg_thing = self._create_thing()
        kg_thing.alias = [Label("Alias 1", EN_US)]

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        alias_diffs = [d for d in differences if d["type"] == "Number of aliases"]
        assert len(alias_diffs) == 1

    def test_different_alias_content(self):
        """Test detection of different alias content."""
        mock_client = MagicMock()

        file_thing = self._create_thing()
        file_thing.alias = [Label("My Alias", EN_US)]

        kg_thing = self._create_thing()
        kg_thing.alias = [Label("Different Alias", EN_US)]

        differences, _, _ = diff_entities(mock_client, file_thing, kg_thing)

        alias_diffs = [d for d in differences if d["type"] == "Alias content"]
        assert len(alias_diffs) == 1
        assert alias_diffs[0]["file"] == "My Alias"

    def test_different_data_properties_count(self):
        """Test detection of different number of data properties."""
        mock_client = MagicMock()

        prop_ref = OntologyPropertyReference.parse("wacom:core#customProp")

        file_thing = self._create_thing()
        file_thing.data_properties[prop_ref] = [DataProperty("value1", prop_ref)]

        kg_thing = self._create_thing()
        # kg_thing has no custom data properties

        _, data_prop_diff, _ = diff_entities(mock_client, file_thing, kg_thing)

        # Should detect missing data property
        missing_diffs = [
            d for d in data_prop_diff if d["type"] == "missing data properties"
        ]
        assert len(missing_diffs) >= 1

    def test_different_data_property_values(self):
        """Test detection of different data property values."""
        mock_client = MagicMock()

        prop_ref = OntologyPropertyReference.parse("wacom:core#customProp")

        file_thing = self._create_thing()
        file_thing.data_properties[prop_ref] = [DataProperty("value1", prop_ref)]

        kg_thing = self._create_thing()
        kg_thing.data_properties[prop_ref] = [DataProperty("value2", prop_ref)]

        _, data_prop_diff, _ = diff_entities(mock_client, file_thing, kg_thing)

        value_diffs = [
            d for d in data_prop_diff if d["type"] == "Different data property values"
        ]
        assert len(value_diffs) == 1
        assert value_diffs[0]["file"] == "value1"

    def test_no_object_properties_diff_without_kg_things(self):
        """Test that object properties are not compared when kg_things is None."""
        mock_client = MagicMock()

        file_thing = self._create_thing()
        kg_thing = self._create_thing()

        # Add object properties to file_thing
        rel_ref = OntologyPropertyReference.parse("wacom:core#relatedTo")
        obj_prop = ObjectProperty(relation=rel_ref)
        obj_prop.outgoing_relations.append("wacom:entity:other")
        file_thing.object_properties[rel_ref] = obj_prop

        _, _, obj_prop_diff = diff_entities(
            mock_client, file_thing, kg_thing, kg_things=None
        )

        # Object properties should not be compared when kg_things is None
        assert len(obj_prop_diff) == 0


class TestIsDifferent:
    """Tests for the is_different function."""

    def _create_thing(
        self,
        labels: List[Label] = None,
        descriptions: List[Description] = None,
    ) -> ThingObject:
        """Helper to create a ThingObject for testing."""
        thing = ThingObject(
            uri="wacom:entity:test",
            label=labels or [Label("Test Entity", EN_US, main=True)],
            description=descriptions or [],
        )
        thing.reference_id = "test-ref-id"
        return thing

    def test_is_different_returns_false_for_identical_entities(self):
        """Test that identical entities return False."""
        mock_client = MagicMock()

        file_thing = self._create_thing(
            labels=[Label("Test", EN_US, main=True)],
            descriptions=[Description("A test entity", EN_US)],
        )
        kg_thing = self._create_thing(
            labels=[Label("Test", EN_US, main=True)],
            descriptions=[Description("A test entity", EN_US)],
        )

        result = is_different(mock_client, file_thing, kg_thing)
        assert result is False

    def test_is_different_returns_true_for_different_entities(self):
        """Test that different entities return True."""
        mock_client = MagicMock()

        file_thing = self._create_thing(labels=[Label("Original", EN_US, main=True)])
        kg_thing = self._create_thing(labels=[Label("Modified", EN_US, main=True)])

        result = is_different(mock_client, file_thing, kg_thing)
        assert result is True

    def test_is_different_detects_data_property_differences(self):
        """Test that data property differences are detected."""
        mock_client = MagicMock()

        prop_ref = OntologyPropertyReference.parse("wacom:core#prop")

        file_thing = self._create_thing()
        file_thing.data_properties[prop_ref] = [DataProperty("value", prop_ref)]

        kg_thing = self._create_thing()
        # kg_thing has no data properties

        result = is_different(mock_client, file_thing, kg_thing)
        assert result is True


class TestDiffEntitiesAsync:
    """Tests for the async diff_entities_async function."""

    def _create_thing(
        self,
        uri: str = "wacom:entity:test",
        labels: List[Label] = None,
        descriptions: List[Description] = None,
        use_for_nel: bool = True,
        use_vector_index: bool = False,
    ) -> ThingObject:
        """Helper to create a ThingObject for testing."""
        thing = ThingObject(
            uri=uri,
            label=labels or [Label("Test Entity", EN_US, main=True)],
            description=descriptions or [],
            use_for_nel=use_for_nel,
            use_vector_index=use_vector_index,
        )
        thing.reference_id = "test-ref-id"
        return thing

    @pytest.mark.asyncio
    async def test_async_identical_entities_no_differences(self):
        """Test that identical entities produce no differences (async)."""
        mock_client = AsyncMock()

        file_thing = self._create_thing(
            labels=[Label("Test", EN_US, main=True)],
            descriptions=[Description("A test entity", EN_US)],
        )
        kg_thing = self._create_thing(
            labels=[Label("Test", EN_US, main=True)],
            descriptions=[Description("A test entity", EN_US)],
        )

        differences, data_prop_diff, obj_prop_diff = await diff_entities_async(
            mock_client, file_thing, kg_thing
        )

        assert len(differences) == 0
        assert len(data_prop_diff) == 0
        assert len(obj_prop_diff) == 0

    @pytest.mark.asyncio
    async def test_async_different_vector_index_flag(self):
        """Test detection of different vector index settings (async)."""
        mock_client = AsyncMock()

        file_thing = self._create_thing(use_vector_index=True)
        kg_thing = self._create_thing(use_vector_index=False)

        differences, _, _ = await diff_entities_async(mock_client, file_thing, kg_thing)

        vector_diffs = [d for d in differences if d["type"] == "Vector index"]
        assert len(vector_diffs) == 1

    @pytest.mark.asyncio
    async def test_async_different_nel_flag(self):
        """Test detection of different NEL settings (async)."""
        mock_client = AsyncMock()

        file_thing = self._create_thing(use_for_nel=False)
        kg_thing = self._create_thing(use_for_nel=True)

        differences, _, _ = await diff_entities_async(mock_client, file_thing, kg_thing)

        nel_diffs = [d for d in differences if d["type"] == "NEL index"]
        assert len(nel_diffs) == 1


class TestIsDifferentAsync:
    """Tests for the async is_different_async function."""

    def _create_thing(
        self,
        labels: List[Label] = None,
        descriptions: List[Description] = None,
    ) -> ThingObject:
        """Helper to create a ThingObject for testing."""
        thing = ThingObject(
            uri="wacom:entity:test",
            label=labels or [Label("Test Entity", EN_US, main=True)],
            description=descriptions or [],
        )
        thing.reference_id = "test-ref-id"
        return thing

    @pytest.mark.asyncio
    async def test_async_is_different_returns_false_for_identical(self):
        """Test that identical entities return False (async)."""
        mock_client = AsyncMock()

        file_thing = self._create_thing(
            labels=[Label("Test", EN_US, main=True)],
            descriptions=[Description("A test entity", EN_US)],
        )
        kg_thing = self._create_thing(
            labels=[Label("Test", EN_US, main=True)],
            descriptions=[Description("A test entity", EN_US)],
        )

        result = await is_different_async(mock_client, file_thing, kg_thing)
        assert result is False

    @pytest.mark.asyncio
    async def test_async_is_different_returns_true_for_different(self):
        """Test that different entities return True (async)."""
        mock_client = AsyncMock()

        file_thing = self._create_thing(labels=[Label("Original", EN_US, main=True)])
        kg_thing = self._create_thing(labels=[Label("Modified", EN_US, main=True)])

        result = await is_different_async(mock_client, file_thing, kg_thing)
        assert result is True
