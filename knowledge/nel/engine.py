# -*- coding: utf-8 -*-
# Copyright © 2021-2023 Wacom. All rights reserved.
from typing import Optional, List, Dict

import requests
from requests import Response
from requests.adapters import HTTPAdapter, Retry

from knowledge.base.entity import LOCALE_TAG, LanguageCode, TEXT_TAG
from knowledge.base.ontology import OntologyClassReference
from knowledge.nel.base import PersonalEntityLinkingProcessor, EntitySource, KnowledgeSource, \
    KnowledgeGraphEntity, EntityType
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import AUTHORIZATION_HEADER_FLAG, CONTENT_TYPE_HEADER_FLAG


class WacomEntityLinkingEngine(PersonalEntityLinkingProcessor):
    """
    Wacom Engine
    ------------
    Performing Wacom's Named entity linking.

    Parameter
    ---------
    service_url: str
        URL of the service
    """
    SERVICE_ENDPOINT: str = 'graph/v1/nel/text'
    SERVICE_URL: str = 'https://private-knowledge.wacom.com'
    LANGUAGES: List[LanguageCode] = [
        LanguageCode('de_DE'),
        LanguageCode('en_US'),
        LanguageCode('ja_JP')
    ]

    def __init__(self, service_url: str = SERVICE_URL, service_endpoint: str = SERVICE_ENDPOINT):
        self.__service_endpoint: str = service_endpoint
        super().__init__(supported_languages=WacomEntityLinkingEngine.LANGUAGES, service_url=service_url)

    def link_personal_entities(self, auth_key: str, text: str, language_code: LanguageCode = 'en_US',
                               max_retries: int = 5) -> List[KnowledgeGraphEntity]:
        """
        Performs Named Entity Linking on a text. It only finds entities which are accessible by the user identified by
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
        entities: List[KnowledgeGraphEntity]
            List of knowledge graph entities.

        Raises
        ------
        WacomServiceException
            If the Named Entity Linking service returns an error code.
        """
        named_entities: List[KnowledgeGraphEntity] = []
        url: str = f'{self.service_url}/{self.__service_endpoint}'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}',
            CONTENT_TYPE_HEADER_FLAG: 'application/json'
        }
        payload: Dict[str, str] = {
            LOCALE_TAG: language_code,
            TEXT_TAG: text
        }
        # Define the retry policy
        retry_policy: Retry = Retry(
            total=max_retries,  # maximum number of retries
            backoff_factor=0.5,  # factor by which to multiply the delay between retries
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
            respect_retry_after_header=True  # respect the Retry-After header
        )

        # Create a session and mount the retry adapter
        with requests.Session() as session:
            retry_adapter = HTTPAdapter(max_retries=retry_policy)
            session.mount("https://", retry_adapter)
            response: Response = session.post(url, headers=headers, json=payload, verify=self.verify_calls)
            if response.ok:
                results: dict = response.json()
                for e in results:
                    entity_types: List[str] = []
                    # --------------------------- Entity content -------------------------------------------------------
                    source: Optional[EntitySource] = None
                    if 'uri' in e:
                        source = EntitySource(e['uri'], KnowledgeSource.WACOM_KNOWLEDGE)
                    # --------------------------- Ontology types -------------------------------------------------------
                    if 'type' in e:
                        entity_types.append(e['type'])
                    # --------------------------------------------------------------------------------------------------
                    start: int = e['startPosition']
                    end: int = e['endPosition']
                    ne: KnowledgeGraphEntity = KnowledgeGraphEntity(ref_text=text[start:end + 1],
                                                                    start_idx=start, end_idx=end,
                                                                    label=e['value'], confidence=0.,
                                                                    source=source, content_link='',
                                                                    ontology_types=entity_types,
                                                                    entity_type=EntityType.PERSONAL_ENTITY)
                    ne.relevant_type = OntologyClassReference.parse(e['type'])
                    named_entities.append(ne)
                return named_entities
        raise WacomServiceException(f'Named entity linking for text:={text}@{language_code}. '
                                    f'Response code:={response.status_code}, exception:= {response.content}')
