# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
from dataclasses import dataclass
from typing import List, Literal, Optional, Dict, Any


@dataclass
class Shard:
    """
    Shard
    -----
    The shard information of the index. The shard information includes the following properties:
    - shard_id: str
    - shard_state: str
    - replica_state: str
    - store_size: str
    - node_name: str
    - num_docs: str
    """

    shard_id: str
    shard_state: str
    replica_state: str
    store_size: str
    node_name: str
    num_docs: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Shard":
        """
        Create a Shard instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing shard fields.

        Returns
        -------
        Shard
            Parsed shard instance.
        """
        return cls(
            shard_id=str(data.get("shard_id", "")),
            shard_state=str(data.get("shard_state", "")),
            replica_state=str(data.get("replica_state", "")),
            store_size=str(data.get("store_size", "")),
            node_name=str(data.get("node_name", "")),
            num_docs=str(data.get("num_docs", "")),
        )


@dataclass
class Node:
    """
    Node
    ----
    Information about a node in the cluster.

    Attributes
    ----------
    id : str
        Node identifier.
    name : str
        Node name.
    master : bool
        Whether this node is a master node.
    version : str
        Elasticsearch/OpenSearch version running on this node.
    """

    id: str
    name: str
    master: bool
    version: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """
        Create a Node instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing node fields.

        Returns
        -------
        Node
            Parsed node instance.
        """
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            master=bool(data.get("master", False)),
            version=str(data.get("version", "")),
        )


@dataclass
class Cluster:
    """
    Cluster
    -------
    Information about the cluster status.

    Attributes
    ----------
    status : str
        Cluster health status (e.g., 'green', 'yellow', 'red').
    number_of_nodes : int
        Total number of nodes in the cluster.
    elected_master : str
        The elected master node identifier.
    master_eligible_nodes : int
        Number of nodes eligible to be master.
    """

    status: str
    number_of_nodes: int
    elected_master: str
    master_eligible_nodes: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cluster":
        """
        Create a Cluster instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing cluster fields.

        Returns
        -------
        Cluster
            Parsed cluster instance.
        """
        return cls(
            status=str(data.get("status", "")),
            number_of_nodes=int(data.get("number_of_nodes", 0)),
            elected_master=str(data.get("elected_master", "")),
            master_eligible_nodes=int(data.get("master_eligible_nodes", 0)),
        )


@dataclass
class Index:
    """
    Index
    -----
    Information about the index status.

    Attributes
    ----------
    unassigned : int
        Number of unassigned shards.
    initializing : int
        Number of initializing shards.
    relocating : int
        Number of relocating shards.
    status : str
        Index health status.
    """

    unassigned: int
    initializing: int
    relocating: int
    status: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Index":
        """
        Create an Index instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing index fields.

        Returns
        -------
        Index
            Parsed index instance.
        """
        return cls(
            unassigned=int(data.get("unassigned", 0)),
            initializing=int(data.get("initializing", 0)),
            relocating=int(data.get("relocating", 0)),
            status=str(data.get("status", "")),
        )


@dataclass
class Condition:
    """
    Condition
    ---------
    Detailed condition information from the health check.

    Attributes
    ----------
    timeout : float
        Timeout value for the health check.
    index_name : str
        Name of the index being checked.
    cluster : Cluster
        Cluster status information.
    index : Index
        Index status information.
    shards : List[Shard]
        List of shard information.
    nodes : List[Node]
        List of node information.
    """

    timeout: float
    index_name: str
    cluster: Cluster
    index: Index
    shards: List[Shard]
    nodes: List[Node]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Condition":
        """
        Create a Condition instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing condition fields.

        Returns
        -------
        Condition
            Parsed condition instance.
        """
        return cls(
            timeout=float(data.get("timeout", 0.0)),
            index_name=str(data.get("index_name", "")),
            cluster=Cluster.from_dict(data.get("cluster", {})),
            index=Index.from_dict(data.get("index", {})),
            shards=[Shard.from_dict(s) for s in data.get("shards", [])],
            nodes=[Node.from_dict(n) for n in data.get("nodes", [])],
        )


@dataclass
class HealthResponse:
    """
    HealthResponse
    --------------
    Response from the index health check endpoint.

    Attributes
    ----------
    healthy : bool
        Whether the index is healthy.
    condition : Condition
        Detailed condition information about the health check.
    """

    healthy: bool
    condition: Condition

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthResponse":
        """
        Create a HealthResponse instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing health response fields.

        Returns
        -------
        HealthResponse
            Parsed health response instance.
        """
        return cls(
            healthy=bool(data.get("healthy", False)),
            condition=Condition.from_dict(data.get("condition", {})),
        )


IndexMode = Literal["document", "word"]


@dataclass
class StreamedDocumentMeta:
    """
    Metadata for a streamed document from the vector database.

    Attributes
    ----------
    concept_type : str
        The concept type/class of the document (e.g., 'wacom:core#Webpage').
    content : str
        The actual text content of the document chunk.
    content_uri : str
        URI identifier for the content source.
    creation : str
        ISO 8601 timestamp of when the document was created.
    locale : str
        Locale code for the document (e.g., 'en_US').
    modification : str
        ISO 8601 timestamp of when the document was last modified.
    chunk_index : Optional[int]
        Index of the chunk within the document (None for single-chunk documents).
    score : Optional[float]
        Relevance score (None for streaming, populated for search results).
    """

    concept_type: str
    content: str
    content_uri: str
    creation: str
    locale: str
    modification: str
    chunk_index: Optional[int] = None
    score: Optional[float] = None

    # Dynamic fields for entity mentions (e.g., 'wacom:education#mentions')
    # These are stored as additional fields in the original dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamedDocumentMeta":
        """
        Create a StreamedDocumentMeta instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing metadata fields.

        Returns
        -------
        StreamedDocumentMeta
            Parsed metadata instance.
        """
        # Extract known fields with proper defaults and type casting
        instance = cls(
            concept_type=str(data.get("concept_type", "")),
            content=str(data.get("content", "")),
            content_uri=str(data.get("content_uri", "")),
            creation=str(data.get("creation", "")),
            locale=str(data.get("locale", "")),
            modification=str(data.get("modification", "")),
            chunk_index=data.get("chunk_index"),
            score=data.get("score"),
        )

        # Add any additional fields that aren't in the dataclass (like entity mentions)
        known_field_names = {
            "concept_type",
            "content",
            "content_uri",
            "creation",
            "locale",
            "modification",
            "chunk_index",
            "score",
        }
        for key, value in data.items():
            if key not in known_field_names:
                setattr(instance, key, value)

        return instance


@dataclass
class IndexDocument:
    """
    A document streamed from the vector database index.

    This represents a single document returned by the streaming endpoint,
    containing the document's content, URI, unique identifier, and metadata.

    Attributes
    ----------
    id : str
        Unique identifier (hash) of the document in the index.
    content : str
        The actual text content of the document.
    content_uri : str
        URI identifier for the content source.
    meta : StreamedDocumentMeta
        Metadata about the document including timestamps, locale, chunk info, etc.

    Examples
    --------
    >>> doc = IndexDocument.from_dict({
    ...     'id': '32b0af53dbb38af8c387def9e9556e7c',
    ...     'content': 'Sample document content...',
    ...     'content_uri': 'a3238ef0-f8a0-493b-8598-97752133994b',
    ...     'meta': {
    ...         'chunk_index': 1,
    ...         'concept_type': 'wacom:core#Webpage',
    ...         'creation': '2026-02-19T15:13:40.402249+00:00',
    ...         'locale': 'en_US'
    ...     }
    ... })
    >>> print(f"Document {doc.id} in {doc.meta.locale}")
    """

    id: str
    content: str
    content_uri: str
    meta: StreamedDocumentMeta

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndexDocument":
        """
        Create a StreamedDocument instance from a dictionary.

        This is the primary method for parsing documents from the NDJSON stream.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing document fields from the streaming API.
            Expected keys: 'id', 'content', 'content_uri', 'meta'

        Returns
        -------
        IndexDocument
            Parsed document instance.

        Raises
        ------
        KeyError
            If required fields are missing from the input dictionary.
        """
        return cls(
            id=data["id"],
            content=data["content"],
            content_uri=data["content_uri"],
            meta=StreamedDocumentMeta.from_dict(data["meta"]),
        )
