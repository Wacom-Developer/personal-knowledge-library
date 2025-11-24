Module knowledge.nel.engine
===========================

Classes
-------

`WacomEntityLinkingEngine(service_url: str = 'https://private-knowledge.wacom.com', service_endpoint: str = 'graph/v1/nel/text')`
:   Wacom Engine
    ------------
    Performing Wacom's Named entity linking.
    
    Parameter
    ---------
    service_url: str
        URL of the service
    service_endpoint: str
        Endpoint of the service

    ### Ancestors (in MRO)

    * knowledge.nel.base.PersonalEntityLinkingProcessor
    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `LANGUAGES: List[knowledge.base.language.LocaleCode]`
    :

    `SERVICE_ENDPOINT: str`
    :

    ### Methods

    `link_personal_entities(self, text: str, language_code: knowledge.base.language.LocaleCode = 'en_US', auth_key: str | None = None, max_retries: int = 5) ‑> List[knowledge.nel.base.KnowledgeGraphEntity]`
    :   Performs Named Entity Linking on a text. It only finds entities which are accessible by the user identified by
        the auth key.
        
        Parameters
        ----------
        text: str
            Text where the entities shall be tagged in.
        language_code: LocaleCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        auth_key: Optional[str]
            If the auth key is set the logged-in user (if any) will be ignored and the auth key will be used.
        max_retries: int
            Maximum number of retries, if the service is not available.
        
        Returns
        -------
        entities: List[KnowledgeGraphEntity]
            List of knowledge graph entities.
        
        Raises
        ------
        WacomServiceException
            If the Named Entity Linking service returns an error code.