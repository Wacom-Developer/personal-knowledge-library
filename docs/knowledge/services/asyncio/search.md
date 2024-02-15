Module knowledge.services.asyncio.search
========================================

Classes
-------

`AsyncSemanticSearchClient(service_url: str, service_endpoint: str = 'vector/api/v1')`
:   Semantic Search Client
    ======================
    Client for searching semantically similar documents and labels.
    
    Parameters
    ----------
    service_url: str
        Service URL for the client.
    service_endpoint: str (Default:= 'vector/v1')
        Service endpoint for the client.

    ### Ancestors (in MRO)

    * knowledge.services.asyncio.base.AsyncServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Methods

    `count_documents(self, locale: knowledge.base.language.LocaleCode, concept_type: Optional[str] = None, auth_key: Optional[str] = None) ‑> int`
    :   Count all documents for a tenant.
        
        Parameters
        ----------
        locale: str
            Locale
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        number_of_docs: int
            Number of documents.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `count_labels(self, locale: str, concept_type: Optional[str] = None, auth_key: Optional[str] = None) ‑> int`
    :   Count all labels entries for a tenant.
        
        Parameters
        ----------
        locale: str
            Locale
        concept_type: Optional[str] (Default:= None)
            Concept type.
        auth_key: Optional[str] (Default:= None)
            If auth key is provided, it will be used for the request.
        
        Returns
        -------
        count: int
            Number of words.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `document_search(self, query: str, locale: str, filters: Optional[Dict[str, Any]] = None, max_results: int = 10, auth_key: Optional[str] = None) ‑> knowledge.base.search.DocumentSearchResponse`
    :   Async Semantic search.
        
        Parameters
        ----------
        query: str
            Query text for the search
        locale: str
            Locale of the text
        filters: Optional[Dict[str, Any]] = None
            Filters for the search
        max_results: int
            Maximum number of results
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        response: DocumentSearchResponse
            Search results response.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `labels_search(self, query: str, locale: str, filters: Optional[Dict[str, Any]] = None, max_results: int = 10, auth_key: Optional[str] = None) ‑> knowledge.base.search.LabelMatchingResponse`
    :   Async search for semantically similar labels.
        
        Parameters
        ----------
        query: str
            Query text for the search
        locale: str
            Locale of the text
        filters: Optional[Dict[str, Any]] = None
            Filters for the search
        max_results: int
            Maximum number of results
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        response: LabelMatchingResponse
            Search results response.

    `retrieve_document_chunks(self, locale: knowledge.base.language.LocaleCode, uri: str, auth_key: Optional[str] = None) ‑> List[knowledge.base.search.VectorDBDocument]`
    :   Retrieve document chunks from vector database. The service is automatically chunking the document into
        smaller parts. The chunks are returned as a list of dictionaries, with metadata and content.
        
        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        document: Dict[str, Any]
            List of document chunks with metadata and content related to the document.
        
        Raises
        ------
        WacomServiceException
            If the request fails.

    `retrieve_labels(self, locale: knowledge.base.language.LocaleCode, uri: str, auth_key: Optional[str] = None) ‑> List[knowledge.base.search.VectorDBDocument]`
    :   Retrieve labels from vector database.
        
        Parameters
        ----------
        locale: LocaleCode
            Locale
        uri: str
            URI of the document
        auth_key: Optional[str] (Default:= None)
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        
        Returns
        -------
        document: List[VectorDBDocument]
            List of labels with metadata and content related to the entity with uri.
        
        Raises
        ------
        WacomServiceException
            If the request fails.