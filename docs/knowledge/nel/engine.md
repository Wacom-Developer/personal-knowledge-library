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

    ### Ancestors (in MRO)

    * knowledge.nel.base.PersonalEntityLinkingProcessor
    * knowledge.services.base.WacomServiceAPIClient
    * knowledge.services.base.RESTAPIClient
    * abc.ABC

    ### Class variables

    `LANGUAGES: list[knowledge.base.entity.LanguageCode]`
    :

    `SERVICE_ENDPOINT: str`
    :

    ### Methods

    `link_personal_entities(self, auth_key: str, text: str, language_code: knowledge.base.entity.LanguageCode = 'en_US', max_retries: int = 5) ‑> list[knowledge.nel.base.KnowledgeGraphEntity]`
    :   Performs Named Entity Linking on a text. It only finds entities which are accessible by the user identified by
        the auth key.
        
        Parameters
        ----------
        auth_key: str
            Auth key identifying a user within the Wacom personal knowledge service.
        text: str
            Text where the entities shall be tagged in.
        language_code: LanguageCode
            ISO-3166 Country Codes and ISO-639 Language Codes in the format '<language_code>_<country>', e.g., 'en_US'.
        max_retries: int
            Maximum number of retries, if the service is not available.
        
        Returns
        -------
        entities: list[KnowledgeGraphEntity]
            List of knowledge graph entities.
        
        Raises
        ------
        WacomServiceException
            If the Named Entity Linking service returns an error code.