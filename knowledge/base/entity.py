# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
import abc
import enum
from typing import Any, List, Dict, Union

from knowledge.base.language import LocaleCode, LanguageCode, EN_US

__all__ = [
    # Exceptions
    "ServiceException",
    "KnowledgeException",
    # Constants
    "RDF_SYNTAX_NS_TYPE",
    "RDF_SCHEMA_COMMENT",
    "RDF_SCHEMA_LABEL",
    "ALIAS_TAG",
    "DATA_PROPERTY_TAG",
    "VALUE_TAG",
    "LANGUAGE_TAG",
    "LOCALE_TAG",
    "DATA_PROPERTIES_TAG",
    "SEND_TO_NEL_TAG",
    "SEND_VECTOR_INDEX_TAG",
    "SOURCE_REFERENCE_ID_TAG",
    "EXTERNAL_USER_ID_TAG",
    "SOURCE_SYSTEM_TAG",
    "OBJECT_PROPERTIES_TAG",
    "OWNER_TAG",
    "OWNER_ID_TAG",
    "GROUP_IDS",
    "LOCALIZED_CONTENT_TAG",
    "STATUS_FLAG_TAG",
    "CONTENT_TAG",
    "URI_TAG",
    "URIS_TAG",
    "FORCE_TAG",
    "ERRORS_TAG",
    "TEXT_TAG",
    "TYPE_TAG",
    "IMAGE_TAG",
    "DESCRIPTION_TAG",
    "COMMENT_TAG",
    "COMMENTS_TAG",
    "DESCRIPTIONS_TAG",
    "REPOSITORY_TAG",
    "DISPLAY_TAG",
    "USE_NEL_TAG",
    "USE_VECTOR_INDEX_TAG",
    "USE_VECTOR_DOCUMENT_INDEX_TAG",
    "USE_FULLTEXT_TAG",
    "TARGETS_TAG",
    "VISIBILITY_TAG",
    "RELATIONS_TAG",
    "INCLUDE_RELATIONS_TAG",
    "LABELS_TAG",
    "IS_MAIN_TAG",
    "DATA_TYPE_TAG",
    "RELATION_TAG",
    "OUTGOING_TAG",
    "INCOMING_TAG",
    "TENANT_RIGHTS_TAG",
    "INFLECTION_CONCEPT_CLASS",
    "INFLECTION_SETTING",
    "INFLECTION_CASE_SENSITIVE",
    "INDEXING_NEL_TARGET",
    "INDEXING_VECTOR_SEARCH_TARGET",
    "INDEXING_VECTOR_SEARCH_DOCUMENT_TARGET",
    "INDEXING_FULLTEXT_TARGET",
    # Classes
    "EntityStatus",
    "LocalizedContent",
    "Label",
    "Description",
]


#  ---------------------------------------- Exceptions -----------------------------------------------------------------
class ServiceException(Exception):
    """Service exception."""


class KnowledgeException(Exception):
    """Knowledge exception."""


#  ---------------------------------------- Constants ------------------------------------------------------------------
RDF_SYNTAX_NS_TYPE: str = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDF_SCHEMA_COMMENT: str = "http://www.w3.org/2000/01/rdf-schema#comment"
RDF_SCHEMA_LABEL: str = "http://www.w3.org/2000/01/rdf-schema#label"
ALIAS_TAG: str = "alias"
DATA_PROPERTY_TAG: str = "literal"
VALUE_TAG: str = "value"
LANGUAGE_TAG: str = "lang"
LOCALE_TAG: str = "locale"
DATA_PROPERTIES_TAG: str = "literals"
SEND_TO_NEL_TAG: str = "sendToNEL"
SEND_VECTOR_INDEX_TAG: str = "sendToVectorIndex"
SOURCE_REFERENCE_ID_TAG: str = "source_reference_id"
EXTERNAL_USER_ID_TAG: str = "external_user_id"
SOURCE_SYSTEM_TAG: str = "source_system"
OBJECT_PROPERTIES_TAG: str = "relations"
OWNER_TAG: str = "owner"
OWNER_ID_TAG: str = "ownerId"
GROUP_IDS: str = "groupIds"
LOCALIZED_CONTENT_TAG: str = "LocalizedContent"
STATUS_FLAG_TAG: str = "status"
CONTENT_TAG: str = "value"
URI_TAG: str = "uri"
URIS_TAG: str = "uris"
FORCE_TAG: str = "force"
ERRORS_TAG: str = "errors"
TEXT_TAG: str = "text"
TYPE_TAG: str = "type"
IMAGE_TAG: str = "image"
DESCRIPTION_TAG: str = "description"
COMMENT_TAG: str = "text"
COMMENTS_TAG: str = "comments"
DESCRIPTIONS_TAG: str = "descriptions"
REPOSITORY_TAG: str = "repository"
DISPLAY_TAG: str = "display"
USE_NEL_TAG: str = "use_for_nel"
USE_VECTOR_INDEX_TAG: str = "use_for_vector_index"
USE_VECTOR_DOCUMENT_INDEX_TAG: str = "use_for_vector_document_index"
USE_FULLTEXT_TAG: str = "user_full_text"
TARGETS_TAG: str = "targets"
VISIBILITY_TAG: str = "visibility"
RELATIONS_TAG: str = "relations"
INCLUDE_RELATIONS_TAG: str = "includeRelations"
LABELS_TAG: str = "labels"
IS_MAIN_TAG: str = "isMain"
DATA_TYPE_TAG: str = "dataType"
RELATION_TAG: str = "relation"
OUTGOING_TAG: str = "out"
INCOMING_TAG: str = "in"
TENANT_RIGHTS_TAG: str = "tenantRights"
INFLECTION_CONCEPT_CLASS: str = "concept"
INFLECTION_SETTING: str = "inflection"
INFLECTION_CASE_SENSITIVE: str = "caseSensitive"
# ------------------------------------------ Indexing targets ----------------------------------------------------------
INDEXING_NEL_TARGET: str = "NEL"
INDEXING_VECTOR_SEARCH_TARGET: str = "VectorSearchWord"
INDEXING_VECTOR_SEARCH_DOCUMENT_TARGET: str = "VectorSearchDocument"
INDEXING_FULLTEXT_TARGET: str = "ElasticSearch"


class EntityStatus(enum.Enum):
    """
    Entity Status
    -------------
    Status of the entity synchronization (client and knowledge graph).
    """

    UNKNOWN = 0
    """Unknown status."""
    CREATED = 1
    """Entity has been created and not yet update."""
    UPDATED = 2
    """Entity has been updated by the client and must be synced."""
    SYNCED = 3
    """State of entity is in sync with knowledge graph."""


class LocalizedContent(abc.ABC):
    """
    Localized content
    -----------------
    Content that is multilingual.

    Parameters
    ----------
    content: str
        Content value
    language_code: LanguageCode (default:= 'en_US')
        ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
    """

    def __init__(self, content: str, language_code: Union[LocaleCode, LanguageCode]) -> None:
        self.__content: str = content
        self.__language_code: Union[LocaleCode, LanguageCode] = language_code

    @property
    def content(self) -> str:
        """String representation of the content."""
        return self.__content

    @content.setter
    def content(self, value: str) -> None:
        self.__content = value

    @property
    def language_code(self) -> Union[LocaleCode, LanguageCode]:
        """Locale"""
        return self.__language_code

    def __repr__(self) -> str:
        return f"{self.content}@{self.language_code}"


class Label(LocalizedContent):
    """
    Label
    -----
    Label that is multilingual.

    Parameters
    ----------
    content: str
        Content value
    language_code: LocaleCode (default:= 'en_US')
        ISO-3166 Country Codes and ISO-639 Language Codes in the format <language_code>_<country>, e.g., en_US.
    main: bool (default:=False)
        Main content
    """

    def __init__(
        self,
        content: str,
        language_code: Union[LocaleCode, LanguageCode] = EN_US,
        main: bool = False,
    ) -> None:
        self.__main: bool = main
        super().__init__(content, language_code)

    @property
    def main(self) -> bool:
        """Flag if the content is the main content or an alias."""
        return self.__main

    @staticmethod
    def create_from_dict(
        dict_label: Dict[str, Any],
        tag_name: str = CONTENT_TAG,
        locale_name: str = LOCALE_TAG,
    ) -> "Label":
        """
        Create a label from a dictionary.
        Parameters
        ----------
        dict_label: Dict[str, Any]
            Dictionary containing the label information.
        tag_name: str
            Tag name of the content.
        locale_name: str
            Tag name of the language code.

        Returns
        -------
        instance: Label
            The Label instance.
        """
        if tag_name not in dict_label:
            raise ValueError("Dict is does not contain a localized label.")
        if locale_name not in dict_label:
            raise ValueError("Dict is does not contain a language code")
        if IS_MAIN_TAG in dict_label:
            return Label(
                dict_label[tag_name],
                LocaleCode(dict_label[locale_name]),
                dict_label[IS_MAIN_TAG],
            )
        return Label(dict_label[tag_name], LocaleCode(dict_label[locale_name]))

    @staticmethod
    def create_from_list(param: List[Dict[str, Any]]) -> List["Label"]:
        """
        Create a list of labels from a list of dictionaries.

        Parameters
        ----------
        param: List[Dict[str, Any]]
            List of dictionaries containing the label information.

        Returns
        -------
        instance: List[Label]
            List of label instances.
        """
        return [Label.create_from_dict(p) for p in param]

    def as_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the instance.

        Returns
        -------
        dict
            Dictionary containing the object's content, language code, and main flag.
            The dictionary keys are ``CONTENT_TAG``, ``LOCALE_TAG``, and ``IS_MAIN_TAG`` respectively.
        """
        return {
            CONTENT_TAG: self.content,
            LOCALE_TAG: self.language_code,
            IS_MAIN_TAG: self.main,
        }


class Description(LocalizedContent):
    """
    Description
    -----------
    Description that is multilingual.

    Parameters
    ----------
    description: str
        Description value
    language_code: LanguageCode (default:= 'en_US')
        Language code of content
    """

    def __init__(self, description: str, language_code: LocaleCode = EN_US) -> None:
        super().__init__(description, language_code)

    @staticmethod
    def create_from_dict(
        dict_description: Dict[str, Any],
        tag_name: str = DESCRIPTION_TAG,
        locale_name: str = LOCALE_TAG,
    ) -> "Description":
        """
        Create a description from a dictionary.

        Parameters
        ----------
        dict_description: Dict[str, Any]
            Dictionary containing the description information.
        tag_name: str
            Tag name of the content.
        locale_name:
            Tag name of the language code.

        Returns
        -------
        instance: Description
            The description instance.
        """
        if tag_name not in dict_description or locale_name not in dict_description:
            raise ValueError("Dict is does not contain a localized label.")
        return Description(dict_description[tag_name], LocaleCode(dict_description[locale_name]))

    @staticmethod
    def create_from_list(param: List[Dict[str, Any]]) -> List["Description"]:
        """Create a list of descriptions from a list of dictionaries.

        Parameters
        ----------
        param: List[Dict[str, Any]]
            List of dictionaries containing the description information.

        Returns
        -------
        instance: List[Description]
            List of description instances.
        """
        return [Description.create_from_dict(p) for p in param]

    def as_dict(self) -> Dict[str, Any]:
        """
        Creates a dictionary representation of the object containing its textual
        content and locale information.

        Returns
        -------
        dict
            A mapping where the description tag is associated with the object's
            content and the locale tag is associated with the object's language
            code.

        Raises
        ------
        None

        Warns
        -----
        None

        Notes
        -----
        None

        Examples
        --------
        None

        References
        ----------
        None

        See Also
        --------
        None
        """
        return {
            DESCRIPTION_TAG: self.content,
            LOCALE_TAG: self.language_code,
        }
