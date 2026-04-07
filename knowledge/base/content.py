# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
from datetime import datetime
from typing import Any, Dict, List, Optional

__all__ = [
    "ContentObject",
]


class ContentObject:
    """
    ContentObject
    -------------
    Represents a content item linked to an entity in the knowledge graph.

    Parameters
    ----------
    content_id: str
        Unique identifier of the content.
    mime_type: str
        MIME type of the stored file.
    tags: List[str]
        Set of tags associated with the content.
    metadata: Dict[str, str]
        Key-value metadata.
    date_added: datetime
        Creation date.
    date_modified: datetime
        The date this content was last modified.
    """

    def __init__(
        self,
        content_id: str,
        mime_type: str,
        tags: List[str],
        metadata: Dict[str, str],
        date_added: datetime,
        date_modified: datetime,
        is_deleted: bool
    ):
        self._id: str = content_id
        self._mime_type: str = mime_type
        self._tags: List[str] = tags
        self._metadata: Dict[str, str] = metadata
        self._date_added: datetime = date_added
        self._date_modified: datetime = date_modified
        self._is_deleted: bool = is_deleted

    @property
    def id(self) -> str:
        """Unique identifier of the content."""
        return self._id

    @property
    def mime_type(self) -> str:
        """MIME type of the stored file."""
        return self._mime_type

    @property
    def tags(self) -> List[str]:
        """Set of tags associated with the content."""
        return self._tags

    @property
    def metadata(self) -> Dict[str, str]:
        """Key-value metadata."""
        return self._metadata

    @property
    def date_added(self) -> datetime:
        """Creation date."""
        return self._date_added

    @property
    def date_modified(self) -> datetime:
        """The date this content was last modified."""
        return self._date_modified

    @property
    def is_deleted(self) -> bool:
        """Indicates whether the content is marked as deleted."""
        return self._is_deleted

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentObject":
        """
        Create a ContentObject instance from a dictionary.

        Parameters
        ----------
        data: Dict[str, Any]
            Response data from the API.

        Returns
        -------
        instance: ContentObject
            Instance of ContentObject.
        """
        return cls(
            content_id=data["id"],
            mime_type=data.get("mimeType", ""),
            tags=list(data.get("tags") or []),
            metadata=dict(data.get("metadata") or {}),
            date_added=datetime.fromisoformat(data["dateAdded"].replace("Z", "+00:00")),
            date_modified=datetime.fromisoformat(data["dateModified"].replace("Z", "+00:00")),
            is_deleted=data.get("isDeleted", False),
        )

    def __repr__(self) -> str:
        return (
            f"ContentObject(id={self.id}, mime_type={self.mime_type}, "
            f"tags={self.tags}, date_added={self.date_added}, date_modified={self.date_modified})"
        )
