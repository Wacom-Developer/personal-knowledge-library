Module knowledge.base.search
============================

Classes
-------

`DocumentCount(count: int, metadata: Dict[str, Any])`
:   Document Count
    ===============
    Response model for the number of documents in the index.
    
    Properties
    ----------
    count: int
        Number of documents.
    metadata: Dict[str, Any]
        Metadata filters.

    ### Instance variables

    `count: int`
    :   Number of documents.

    `metadata: Dict[str, Any]`
    :   Metadata filters.

`DocumentSearchResponse(results: List[knowledge.base.search.DocumentSearchResult], max_results: int = 10, stats: Optional[knowledge.base.search.DocumentSearchStats] = None)`
:   DocumentSearchResponse
    ======================
    Response model for semantic search service.
    
    Properties
    ----------
    results: List[DocumentSearchResult]
        Search results
    max_results: int
        Maximum number of results
    stats: Optional[PerformanceStats]
        Performance stats

    ### Static methods

    `from_dict(data: Dict[str, Any]) ‑> knowledge.base.search.DocumentSearchResponse`
    :   Create a DocumentSearchResponse from a dictionary.
        Parameters
        ----------
        data: Dict[str, Any]
            Dictionary with the response data.
        
        Returns
        -------
        DocumentSearchResponse
            Document search response.

    ### Instance variables

    `max_results: int`
    :   Maximum number of results.

    `results: List[knowledge.base.search.DocumentSearchResult]`
    :   List of search results.

    `stats: Optional[knowledge.base.search.DocumentSearchStats]`
    :   Performance stats.

`DocumentSearchResult(score: float, content_uri: str, metadata: Dict[str, Any], content: str)`
:   DocumentSearchResult
    ====================
    This is a search result model.
    
    Properties
    ----------
    score: float
        Score of the search result.
    content_uri: str
        Unique identifier of the entity.
    metadata: Dict[str, Any]
        Metadata of the search result.
    content_chunk: str
        Content chunk of the search result.
    concept_type: OntologyClassReference
        Concept type of the search result.
    locale: LocaleCode
        Locale of the search result.

    ### Instance variables

    `concept_type: knowledge.base.ontology.OntologyClassReference`
    :   Concept type of the search result.

    `content_chunk: str`
    :   Chunk of the document.

    `content_uri: str`
    :   Unique identifier of the content.

    `locale: knowledge.base.language.LocaleCode`
    :   Locale of the search result.

    `metadata: Dict[str, Any]`
    :   Metadata of the search result.

    `score: float`
    :   Score of the search result.

`DocumentSearchStats(stats: Dict[str, Any])`
:   DocumentSearchStats
    ====================
    This is a performance stats model for document search.
    
    Properties
    ----------
    locale_code: LocaleCode
        Performance for the model with the given locale.
    model_name: str
        Name of the model used for the search.
    top_k: int
        Top-k results requested.
    model_loading_time: float
        Loading time in milliseconds for the embedding model.
    embedding_time: float
        Embedding time in milliseconds for the search query.
    vector_db_response_time: float
        Response time in milliseconds for the vector database.
    preprocessing_time: float
        Preprocessing time in milliseconds for search query.

    ### Ancestors (in MRO)

    * knowledge.base.search.PerformanceStats

    ### Instance variables

    `preprocessing_time: float`
    :   Preprocessing time in milliseconds for search query.

`LabelCount(count: int, metadata: Dict[str, Any])`
:   LabelCount
    =========
    Request model to rebuild the index for a specific tenant.

    ### Instance variables

    `count: int`
    :   Number of labels.

    `metadata: Dict[str, Any]`
    :   Metadata filters.

`LabelMatchingResponse(results: List[knowledge.base.search.LabelSearchResult], max_results: int = 10, stats: Optional[knowledge.base.search.LabelSearchStats] = None)`
:   SemanticSearchResponse
    ======================
    Response model for semantic search service.
    
    Properties
    ----------
    results: List[LabelSearchResult]
        Search results
    max_results: int
        Maximum number of results
    stats: Optional[LabelSearchStats]
        Performance stats

    ### Static methods

    `from_dict(data: Dict[str, Any])`
    :   Create a LabelMatchingResponse from a dictionary.
        Parameters
        ----------
        data: Dict[str, Any]
            Dictionary with the response data.
        
        Returns
        -------
        LabelMatchingResponse
            Label matching response.

    ### Instance variables

    `max_results: int`
    :   Maximum number of results.

    `results: List[knowledge.base.search.LabelSearchResult]`
    :   List of label search results.

    `stats: Optional[knowledge.base.search.LabelSearchStats]`
    :   Performance stats.

`LabelSearchResult(score: float, content_uri: str, metadata: Dict[str, Any], content: str)`
:   LabelSearchResult
    =================
    This is a search result model.
    
    Properties
    ----------
    score: float
        Score of the search result.
    entity_uri: str
        Unique identifier of the entity.
    label: str
        Label of the search result.
    locale: LocaleCode
        Locale of the search result.
    concept_type: OntologyClassReference
        Concept type of the search result.
    metadata: Dict[str, Any]
        Metadata of the search result.

    ### Instance variables

    `concept_type: knowledge.base.ontology.OntologyClassReference`
    :   Concept type of the search result.

    `entity_uri: str`
    :   Unique identifier of the entity.

    `label: knowledge.base.entity.Label`
    :   Label of the search result.

    `locale: knowledge.base.language.LocaleCode`
    :   Locale of the search result.

    `metadata: Dict[str, Any]`
    :   Metadata of the search result.

    `score: float`
    :   Score of the search result.

`LabelSearchStats(stats: Dict[str, Any])`
:   LabelSearchStats
    ================
    This is a performance stats model for label search.
    
    Properties
    ----------
    locale_code: LocaleCode
        Performance for the model with the given locale.
    model_name: str
        Name of the model used for the search.
    top_k: int
        Top-k results requested.
    model_loading_time: float
        Loading time in milliseconds for the embedding model.
    embedding_time: float
        Embedding time in milliseconds for the search query.
    vector_db_response_time: float
        Response time in milliseconds for the vector database.
    tokenizer_time: float
        Tokenizer time in milliseconds for search query.
    number_of_tokens: int
        Number of tokens in the search query.

    ### Ancestors (in MRO)

    * knowledge.base.search.PerformanceStats

    ### Instance variables

    `number_of_tokens: int`
    :   Number of tokens in the search query.

    `tokenizer_time: float`
    :   Tokenizer time in milliseconds for search query.

`PerformanceStats(stats: Dict[str, Any])`
:   PerformanceStats
    ================
    This is a performance stats model.
    
    Properties
    ----------
    locale_code: LocaleCode
        Performance for the model with the given locale.
    model_name: str
        Name of the model used for the search.
    top_k: int
        Top-k results requested.
    model_loading_time: float
        Loading time in milliseconds for the embedding model.
    embedding_time: float
        Embedding time in milliseconds for the search query.
    vector_db_response_time: float
        Response time in milliseconds for the vector database.

    ### Descendants

    * knowledge.base.search.DocumentSearchStats
    * knowledge.base.search.LabelSearchStats

    ### Instance variables

    `embedding_time: float`
    :   Embedding time in milliseconds for the search query.

    `locale_code: knowledge.base.language.LocaleCode`
    :   Performance for the model with the given locale.

    `model_loading_time: float`
    :   Loading time in milliseconds for the embedding model.

    `model_name: str`
    :   Name of the model used for the search.

    `overall_time: float`
    :   Overall time in milliseconds for the search query.

    `top_k: int`
    :   Top-k results requested.

    `vector_db_response_time: float`
    :   Response time in milliseconds for the vector database.

`VectorDBDocument(data: Dict[str, Any])`
:   VectorDBDocument
    ================
    Document model for the vector database.
    
    Properties
    ----------

    ### Instance variables

    `content: str`
    :   Content of the document.

    `id: str`
    :   ID of the document.

    `metadata: Dict[str, Any]`
    :   Metadata of the document.

    `uri: str`
    :   URI of the document.