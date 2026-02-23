Module knowledge.base.index
===========================

Classes
-------

`Cluster(status: str, number_of_nodes: int, elected_master: str, master_eligible_nodes: int)`
:   Cluster
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

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.index.Cluster`
    :   Create a Cluster instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing cluster fields.
        
        Returns
        -------
        Cluster
            Parsed cluster instance.

    ### Instance variables

    `elected_master: str`
    :   The type of the None singleton.

    `master_eligible_nodes: int`
    :   The type of the None singleton.

    `number_of_nodes: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

`Condition(timeout: float, index_name: str, cluster: knowledge.base.index.Cluster, index: knowledge.base.index.Index, shards: List[knowledge.base.index.Shard], nodes: List[knowledge.base.index.Node])`
:   Condition
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

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.index.Condition`
    :   Create a Condition instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing condition fields.
        
        Returns
        -------
        Condition
            Parsed condition instance.

    ### Instance variables

    `cluster: knowledge.base.index.Cluster`
    :   The type of the None singleton.

    `index: knowledge.base.index.Index`
    :   The type of the None singleton.

    `index_name: str`
    :   The type of the None singleton.

    `nodes: List[knowledge.base.index.Node]`
    :   The type of the None singleton.

    `shards: List[knowledge.base.index.Shard]`
    :   The type of the None singleton.

    `timeout: float`
    :   The type of the None singleton.

`HealthResponse(healthy: bool, condition: knowledge.base.index.Condition)`
:   HealthResponse
    --------------
    Response from the index health check endpoint.
    
    Attributes
    ----------
    healthy : bool
        Whether the index is healthy.
    condition : Condition
        Detailed information about the health check.

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.index.HealthResponse`
    :   Create a HealthResponse instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing health response fields.
        
        Returns
        -------
        HealthResponse
            Parsed health response instance.

    ### Instance variables

    `condition: knowledge.base.index.Condition`
    :   The type of the None singleton.

    `healthy: bool`
    :   The type of the None singleton.

`Index(unassigned: int, initializing: int, relocating: int, status: str)`
:   Index
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

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.index.Index`
    :   Create an Index instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing index fields.
        
        Returns
        -------
        Index
            Parsed index instance.

    ### Instance variables

    `initializing: int`
    :   The type of the None singleton.

    `relocating: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `unassigned: int`
    :   The type of the None singleton.

`IndexDocument(id: str, content: str, content_uri: str, meta: knowledge.base.index.StreamedDocumentMeta)`
:   A document streamed from the vector database index.
    
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

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.index.IndexDocument`
    :   Create a StreamedDocument instance from a dictionary.
        
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

    ### Instance variables

    `content: str`
    :   The type of the None singleton.

    `content_uri: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `meta: knowledge.base.index.StreamedDocumentMeta`
    :   The type of the None singleton.

`Node(id: str, name: str, master: bool, version: str)`
:   Node
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

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.index.Node`
    :   Create a Node instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing node fields.
        
        Returns
        -------
        Node
            Parsed node instance.

    ### Instance variables

    `id: str`
    :   The type of the None singleton.

    `master: bool`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `version: str`
    :   The type of the None singleton.

`Shard(shard_id: str, shard_state: str, replica_state: str, store_size: str, node_name: str, num_docs: str)`
:   Shard
    -----
    The shard information of the index. The shard information includes the following properties:
    - shard_id: str
    - shard_state: str
    - replica_state: str
    - store_size: str
    - node_name: str
    - num_docs: str

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.index.Shard`
    :   Create a Shard instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing shard fields.
        
        Returns
        -------
        Shard
            Parsed shard instance.

    ### Instance variables

    `node_name: str`
    :   The type of the None singleton.

    `num_docs: str`
    :   The type of the None singleton.

    `replica_state: str`
    :   The type of the None singleton.

    `shard_id: str`
    :   The type of the None singleton.

    `shard_state: str`
    :   The type of the None singleton.

    `store_size: str`
    :   The type of the None singleton.

`StreamedDocumentMeta(concept_type: str, content: str, content_uri: str, creation: str, locale: str, modification: str, chunk_index: int | None = None, score: float | None = None)`
:   Metadata for a streamed document from the vector database.
    
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

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.index.StreamedDocumentMeta`
    :   Create a StreamedDocumentMeta instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing metadata fields.
        
        Returns
        -------
        StreamedDocumentMeta
            Parsed metadata instance.

    ### Instance variables

    `chunk_index: int | None`
    :   The type of the None singleton.

    `concept_type: str`
    :   The type of the None singleton.

    `content: str`
    :   The type of the None singleton.

    `content_uri: str`
    :   The type of the None singleton.

    `creation: str`
    :   The type of the None singleton.

    `locale: str`
    :   The type of the None singleton.

    `modification: str`
    :   The type of the None singleton.

    `score: float | None`
    :   The type of the None singleton.