# -*- coding: utf-8 -*-
# Copyright © 2025-present Wacom. All rights reserved.
"""
Unit tests for knowledge/base/access.py

These tests verify the access rights classes.
"""

from knowledge.base.access import AccessRight, TenantAccessRight, GroupAccessRight


class TestAccessRight:
    """Tests for AccessRight class."""

    def test_create_with_no_rights(self):
        """Test creating AccessRight with no permissions."""
        rights = AccessRight(read=False, write=False, delete=False)

        assert rights.read is False
        assert rights.write is False
        assert rights.delete is False

    def test_create_with_all_rights(self):
        """Test creating AccessRight with all permissions."""
        rights = AccessRight(read=True, write=True, delete=True)

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is True

    def test_create_with_read_only(self):
        """Test creating AccessRight with read-only permission."""
        rights = AccessRight(read=True, write=False, delete=False)

        assert rights.read is True
        assert rights.write is False
        assert rights.delete is False

    def test_create_with_read_write(self):
        """Test creating AccessRight with read/write permissions."""
        rights = AccessRight(read=True, write=True, delete=False)

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is False

    def test_setter_read(self):
        """Test read setter."""
        rights = AccessRight(read=False, write=False, delete=False)
        assert rights.read is False

        rights.read = True
        assert rights.read is True

    def test_setter_write(self):
        """Test write setter."""
        rights = AccessRight(read=False, write=False, delete=False)
        assert rights.write is False

        rights.write = True
        assert rights.write is True

    def test_setter_delete(self):
        """Test delete setter."""
        rights = AccessRight(read=False, write=False, delete=False)
        assert rights.delete is False

        rights.delete = True
        assert rights.delete is True

    def test_repr_no_rights(self):
        """Test string representation with no rights."""
        rights = AccessRight(read=False, write=False, delete=False)
        result = repr(rights)
        assert result == "[]"

    def test_repr_read_only(self):
        """Test string representation with read-only."""
        rights = AccessRight(read=True, write=False, delete=False)
        result = repr(rights)
        assert "Read" in result

    def test_repr_read_write(self):
        """Test string representation with read and write."""
        rights = AccessRight(read=True, write=True, delete=False)
        result = repr(rights)
        assert "Read" in result
        assert "Write" in result

    def test_repr_all_rights(self):
        """Test string representation with all rights."""
        rights = AccessRight(read=True, write=True, delete=True)
        result = repr(rights)
        assert "Read" in result
        assert "Write" in result
        assert "Delete" in result

    def test_repr_delete_only(self):
        """Test string representation with delete only."""
        rights = AccessRight(read=False, write=False, delete=True)
        result = repr(rights)
        assert "Delete" in result

    def test_to_list_empty(self):
        """Test to_list with no rights."""
        rights = AccessRight(read=False, write=False, delete=False)
        result = rights.to_list()
        assert result == []

    def test_to_list_all_rights(self):
        """Test to_list with all rights."""
        rights = AccessRight(read=True, write=True, delete=True)
        result = rights.to_list()

        assert len(result) == 3
        assert "Read" in result
        assert "Write" in result
        assert "Delete" in result

    def test_to_list_read_only(self):
        """Test to_list with read-only."""
        rights = AccessRight(read=True, write=False, delete=False)
        result = rights.to_list()

        assert len(result) == 1
        assert "Read" in result

    def test_class_constants(self):
        """Test class constants."""
        assert AccessRight.READ == "Read"
        assert AccessRight.WRITE == "Write"
        assert AccessRight.DELETE == "Delete"


class TestTenantAccessRight:
    """Tests for TenantAccessRight class."""

    def test_create_default_no_rights(self):
        """Test creating TenantAccessRight with default (no) permissions."""
        rights = TenantAccessRight()

        assert rights.read is False
        assert rights.write is False
        assert rights.delete is False

    def test_create_with_all_rights(self):
        """Test creating TenantAccessRight with all permissions."""
        rights = TenantAccessRight(read=True, write=True, delete=True)

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is True

    def test_create_with_partial_rights(self):
        """Test creating TenantAccessRight with partial permissions."""
        rights = TenantAccessRight(read=True, write=True)

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is False

    def test_parse_empty_list(self):
        """Test parsing empty list creates no rights."""
        rights = TenantAccessRight.parse([])

        assert rights.read is False
        assert rights.write is False
        assert rights.delete is False

    def test_parse_read_only(self):
        """Test parsing list with Read creates read-only rights."""
        rights = TenantAccessRight.parse(["Read"])

        assert rights.read is True
        assert rights.write is False
        assert rights.delete is False

    def test_parse_read_write(self):
        """Test parsing list with Read and Write."""
        rights = TenantAccessRight.parse(["Read", "Write"])

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is False

    def test_parse_all_rights(self):
        """Test parsing list with all rights."""
        rights = TenantAccessRight.parse(["Read", "Write", "Delete"])

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is True

    def test_parse_with_extra_values(self):
        """Test parsing list with extra unknown values."""
        rights = TenantAccessRight.parse(["Read", "Unknown", "Write"])

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is False

    def test_inherits_from_access_right(self):
        """Test that TenantAccessRight inherits from AccessRight."""
        rights = TenantAccessRight()
        assert isinstance(rights, AccessRight)

    def test_to_list_round_trip(self):
        """Test that to_list output can be parsed back."""
        original = TenantAccessRight(read=True, write=True, delete=False)
        rights_list = original.to_list()
        parsed = TenantAccessRight.parse(rights_list)

        assert parsed.read == original.read
        assert parsed.write == original.write
        assert parsed.delete == original.delete


class TestGroupAccessRight:
    """Tests for GroupAccessRight class."""

    def test_create_default_no_rights(self):
        """Test creating GroupAccessRight with default (no) permissions."""
        rights = GroupAccessRight()

        assert rights.read is False
        assert rights.write is False
        assert rights.delete is False

    def test_create_with_all_rights(self):
        """Test creating GroupAccessRight with all permissions."""
        rights = GroupAccessRight(read=True, write=True, delete=True)

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is True

    def test_create_with_partial_rights(self):
        """Test creating GroupAccessRight with partial permissions."""
        rights = GroupAccessRight(read=True)

        assert rights.read is True
        assert rights.write is False
        assert rights.delete is False

    def test_parse_empty_list(self):
        """Test parsing empty list creates no rights."""
        rights = GroupAccessRight.parse([])

        assert rights.read is False
        assert rights.write is False
        assert rights.delete is False

    def test_parse_read_only(self):
        """Test parsing list with Read creates read-only rights."""
        rights = GroupAccessRight.parse(["Read"])

        assert rights.read is True
        assert rights.write is False
        assert rights.delete is False

    def test_parse_all_rights(self):
        """Test parsing list with all rights."""
        rights = GroupAccessRight.parse(["Read", "Write", "Delete"])

        assert rights.read is True
        assert rights.write is True
        assert rights.delete is True

    def test_inherits_from_access_right(self):
        """Test that GroupAccessRight inherits from AccessRight."""
        rights = GroupAccessRight()
        assert isinstance(rights, AccessRight)

    def test_to_list_round_trip(self):
        """Test that to_list output can be parsed back."""
        original = GroupAccessRight(read=True, write=False, delete=True)
        rights_list = original.to_list()
        parsed = GroupAccessRight.parse(rights_list)

        assert parsed.read == original.read
        assert parsed.write == original.write
        assert parsed.delete == original.delete

    def test_group_and_tenant_are_separate(self):
        """Test that group and tenant rights are separate classes."""
        tenant_rights = TenantAccessRight(read=True)
        group_rights = GroupAccessRight(write=True)

        assert isinstance(tenant_rights, TenantAccessRight)
        assert isinstance(group_rights, GroupAccessRight)
        assert not isinstance(tenant_rights, GroupAccessRight)
        assert not isinstance(group_rights, TenantAccessRight)
