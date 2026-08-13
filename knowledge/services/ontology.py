# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom. All rights reserved.
import urllib.parse
from http import HTTPStatus
from typing import Any, Optional, Dict, Tuple, List, Union, cast

from requests import Response

from knowledge.base.entity import (
    FORCE_TAG,
    INFLECTION_CASE_SENSITIVE,
    INFLECTION_CONCEPT_CLASS,
    INFLECTION_SETTING,
)
from knowledge.base.ontology import (
    OntologyClassReference,
    OntologyPropertyReference,
    OntologyProperty,
    OntologyClass,
    PropertyType,
    THING_CLASS,
    DataPropertyType,
    ImportResponse,
    InflectionLevel,
    InflectionSetting,
    Comment,
    OntologyContext,
    OntologyLabel,
    RESOURCE,
)
from knowledge.services import DEFAULT_MAX_RETRIES, DEFAULT_BACKOFF_FACTOR
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException, handle_error

__all__ = ["OntologyService"]

# ------------------------------------------------- Constants ----------------------------------------------------------
BASE_URI_TAG: str = "baseUri"
COMMENTS_TAG: str = "comments"
USER_AGENT_TAG: str = "User-Agent"
DOMAIN_TAG: str = "domains"
ICON_TAG: str = "icon"
INVERSE_OF_TAG: str = "inverseOf"
KIND_TAG: str = "kind"
LABELS_TAG: str = "labels"
LANGUAGE_CODE: str = "lang"
NAME_TAG: str = "name"
CONTEXT_TAG: str = "context"
RANGE_TAG: str = "ranges"
SUB_CLASS_OF_TAG: str = "subClassOf"
SUB_PROPERTY_OF_TAG: str = "subPropertyOf"
LISTING_MODE_PARAM: str = "listingMode"
VERSION_PARAM: str = "version"
START_AT_PARAM: str = "startAt"
END_AT_PARAM: str = "endAt"
TEXT_TAG: str = "value"
DEFAULT_TIMEOUT: int = 30


def _resolve_range_iri(range_value: Union[OntologyClassReference, DataPropertyType]) -> str:
    """Resolve a property range entry to its IRI string.

    Object-property ranges are ontology classes; data-property ranges are XSD data types.

    Parameters
    ----------
    range_value: Union[OntologyClassReference, DataPropertyType]
        Range entry to resolve.

    Returns
    -------
    iri: str
        IRI of the range entry.
    """
    if isinstance(range_value, DataPropertyType):
        return str(range_value.value)
    return range_value.iri


class OntologyService(WacomServiceAPIClient):
    """
    Ontology API Client
    -------------------
    Client to access the ontology service. Offers the following functionality:
    - Listing class names and property names
    - Create new ontology types
    - Update ontology types

    Parameters
    ----------
    application_name: str
        Name of the application.
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    max_retries: int
        Maximum number of retries for failed requests.
    backoff_factor: float
        Backoff factor between retries.

    Examples
    --------
    >>> from knowledge.services.ontology import OntologyService
    >>>
    >>> # Initialize the client
    >>> client = OntologyService(
    ...     service_url="https://private-knowledge.wacom.com"
    ... )
    >>> client.login(tenant_api_key="<tenant_key>", external_user_id="<user_id>")
    >>>
    >>> # Get ontology context
    >>> context = client.context()
    >>>
    >>> # List all concepts (classes)
    >>> concepts = client.concepts()
    >>> for concept in concepts:
    ...     print(f"Class: {concept.iri}")
    >>>
    >>> # List all properties
    >>> properties = client.properties()
    """

    CONTEXT_ENDPOINT: str = "context"
    CONCEPTS_ENDPOINT: str = "concepts"
    PROPERTIES_ENDPOINT: str = "properties"
    RDF_ENDPOINT: str = "context/{}/versions/rdf"
    PROPERTY_ENDPOINT: str = "context/{}/properties/{}"

    def __init__(
        self,
        service_url: str,
        application_name: str = "Ontology Service",
        base_auth_url: Optional[str] = None,
        service_endpoint: str = "ontology/v1",
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        super().__init__(
            service_url=service_url,
            application_name=application_name,
            base_auth_url=base_auth_url,
            service_endpoint=service_endpoint,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    def context(
        self,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Optional[OntologyContext]:
        """
        Getting the information on the context.

        Parameters
        ----------
        auth_key: Optional[str] = None
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        context_description: Optional[OntologyContext]
            Context of the Ontology
        """
        try:
            contexts: List[OntologyContext] = self.contexts(auth_key=auth_key, timeout=timeout)
        except WacomServiceException:
            # Preserves the historic contract of this method: None rather than an exception.
            return None
        return contexts[0] if contexts else None

    def contexts(
        self,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[OntologyContext]:
        """
        List all ontology contexts of the tenant.

        Parameters
        ----------
        auth_key: Optional[str] = None
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Returns
        -------
        contexts: List[OntologyContext]
            Contexts of the ontology. Empty if the tenant has none.

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        response: Response = self.request_session.get(
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}",
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if not response.ok:
            raise handle_error("Failed to retrieve the contexts", response)
        payload: Any = response.json()
        # The service returns a list of context envelopes; older deployments returned a single one.
        envelopes: List[Dict[str, Any]] = payload if isinstance(payload, list) else [payload]
        return [OntologyContext.from_dict(envelope) for envelope in envelopes]

    def context_metadata(
        self,
        context: str,
        version: Optional[int] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[InflectionSetting]:
        """
        Getting the meta-data on the context.

        Parameters
        ----------
        context: str
            Name of the context.
        version: Optional[int] [default:= None]
            Version of the context. If None, the latest version is used.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        list_inflection_settings: List[InflectionSetting]
            List of inflection settings.
        """
        params: Dict[str, int] = {} if version is None else {VERSION_PARAM: version}
        context_url: str = urllib.parse.quote_plus(context)
        response: Response = self.request_session.get(
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/metadata",
            params=params,
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return [
                InflectionSetting.from_dict(c)
                for c in response.json()
                if c.get("concept") is not None and not c.get("concept").startswith("http")
            ]
        raise handle_error("Failed to retrieve context metadata", response)

    def concepts(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[Tuple[OntologyClassReference, Optional[OntologyClassReference]]]:
        """Retrieve all concept classes.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of the ontology
        auth_key: Optional[str] = None
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        concepts: List[Tuple[OntologyClassReference, Optional[OntologyClassReference]]]
            List of ontology classes. Tuple<Classname, Superclass>
        """
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}"
        )
        response: Response = self.request_session.get(
            url,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            response_list: List[Tuple[OntologyClassReference, Optional[OntologyClassReference]]] = []
            result = response.json()
            for struct in result:
                response_list.append(
                    (
                        OntologyClassReference.parse(struct[NAME_TAG]),
                        (
                            None
                            if struct[SUB_CLASS_OF_TAG] is None
                            else OntologyClassReference.parse(struct[SUB_CLASS_OF_TAG])
                        ),
                    )
                )
            return response_list
        raise handle_error("Failed to retrieve concepts", response)

    def concepts_types(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[OntologyClass]:
        """Retrieve all concept class types.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of the ontology
        auth_key: Optional[str] = None
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        concepts: List[OntologyClass]
            List of ontology classes.
        """
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}"
        )
        response: Response = self.request_session.get(
            url,
            verify=self.verify_calls,
            params={LISTING_MODE_PARAM: "Full"},
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            response_list: List[OntologyClass] = []
            for struct in response.json():
                if struct[NAME_TAG] != RESOURCE:
                    response_list.append(OntologyClass.from_dict(struct))
            return response_list
        raise handle_error("Failed to retrieve concepts", response)

    def properties(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[Tuple[OntologyPropertyReference, Optional[OntologyPropertyReference]]]:
        """List all properties.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        contexts: List[Tuple[OntologyPropertyReference, Optional[OntologyPropertyReference]]]
            List of ontology contexts
        """
        context_url: str = urllib.parse.quote_plus(context)
        response: Response = self.request_session.get(
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/"
            f"{context_url}/{OntologyService.PROPERTIES_ENDPOINT}",
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        # Return an empty list if the NOT_FOUND is reported
        if response.status_code == HTTPStatus.NOT_FOUND:
            return []
        if response.ok:
            response_list: List[Tuple[OntologyPropertyReference, Optional[OntologyPropertyReference]]] = []
            for c in response.json():
                response_list.append(
                    (
                        OntologyPropertyReference.parse(c[NAME_TAG]),
                        (
                            None
                            if c[SUB_PROPERTY_OF_TAG] is None or c.get(SUB_PROPERTY_OF_TAG) == ""
                            else OntologyPropertyReference.parse(c[SUB_PROPERTY_OF_TAG])
                        ),
                    )
                )
            return response_list
        raise handle_error("Failed to retrieve properties", response)

    def properties_types(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[OntologyProperty]:
        """List all properties types.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        contexts: List[OntologyProperty]
            List of ontology contexts
        """
        context_url: str = urllib.parse.quote_plus(context)
        response: Response = self.request_session.get(
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/"
            f"{context_url}/{OntologyService.PROPERTIES_ENDPOINT}",
            params={LISTING_MODE_PARAM: "Full"},
            timeout=timeout,
            verify=self.verify_calls,
            overwrite_auth_token=auth_key,
        )
        # Return empty list if the NOT_FOUND is reported
        if response.status_code == HTTPStatus.NOT_FOUND:
            return []
        if response.ok:
            response_list: List[OntologyProperty] = []
            for c in response.json():
                response_list.append((OntologyProperty.from_dict(c)))
            return response_list
        raise handle_error("Failed to retrieve properties", response)

    def concept(
        self,
        context: str,
        concept_name: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> OntologyClass:
        """Retrieve a concept instance.

        **Remark:**
        Works for users with the role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context
        concept_name: str
            IRI of the concept
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        Returns
        -------
        instance: OntologyClass
            Instance of the concept
        """
        context_url: str = urllib.parse.quote_plus(context)
        concept_url: str = urllib.parse.quote_plus(concept_name)
        response: Response = self.request_session.get(
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}"
            f"/{OntologyService.CONCEPTS_ENDPOINT}/{concept_url}",
            overwrite_auth_token=auth_key,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if response.ok:
            result: Dict[str, Any] = response.json()
            return OntologyClass.from_dict(result)
        raise handle_error("Failed to retrieve concept", response)

    def property(
        self,
        context: str,
        property_name: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> OntologyProperty:
        """Retrieve a property instance.

        **Remark:**
        Works for users with role 'User' and 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context
        property_name: str
            IRI of the property
        auth_key: Optional[str] [default:= None]
            If an auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        instance: OntologyProperty
            Instance of the property
        """
        context_url: str = urllib.parse.quote_plus(context)
        concept_url: str = urllib.parse.quote_plus(property_name)
        param: str = f"context/{context_url}/properties/{concept_url}"
        response: Response = self.request_session.get(
            f"{self.service_base_url}{param}",
            overwrite_auth_token=auth_key,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if response.ok:
            return OntologyProperty.from_dict(response.json())
        raise handle_error("Failed to retrieve property", response)

    def create_concept(
        self,
        context: str,
        reference: OntologyClassReference,
        subclass_of: OntologyClassReference = THING_CLASS,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, str]:
        """Create a concept class.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        subclass_of: OntologyClassReference (default:=wacom:core#Thing)
            Super class of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        result: Dict[str, str]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        payload: Dict[str, Any] = {
            SUB_CLASS_OF_TAG: subclass_of.iri,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}"
        )

        response: Response = self.request_session.post(
            url,
            overwrite_auth_token=auth_key,
            json=payload,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if response.ok:
            result_dict: Dict[str, str] = response.json()
            return result_dict
        raise handle_error("Failed to create concept", response, payload=payload)

    def update_concept(
        self,
        context: str,
        reference: OntologyClassReference,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Update the labels, comments and icon of a concept class.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        The superclass of a concept cannot be changed through this API; the service accepts
        only labels, comments and the icon.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Reference of the concept to update
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        payload: Dict[str, Any] = {
            LABELS_TAG: [{TEXT_TAG: la.content, LANGUAGE_CODE: la.language_code} for la in labels or []],
            COMMENTS_TAG: [{TEXT_TAG: co.content, LANGUAGE_CODE: co.language_code} for co in comments or []],
            ICON_TAG: icon,
        }
        context_url: str = urllib.parse.quote_plus(context)
        concept_url: str = urllib.parse.quote_plus(reference.iri)
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}/{concept_url}"
        )
        response: Response = self.request_session.patch(
            url,
            overwrite_auth_token=auth_key,
            json=payload,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if not response.ok:
            raise handle_error("Failed to update concept", response, payload=payload)

    def set_concept_metadata(
        self,
        context: str,
        reference: OntologyClassReference,
        inflection: InflectionLevel,
        case_sensitive: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Set the Named Entity Linking metadata of a concept class.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Reference of the concept
        inflection: InflectionLevel
            Level of inflection handling applied to entity labels of the class
        case_sensitive: bool (default:= False)
            Treat entity labels of the class as case-sensitive
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        payload: Dict[str, Any] = {
            INFLECTION_CONCEPT_CLASS: reference.iri,
            INFLECTION_SETTING: inflection.value,
            INFLECTION_CASE_SENSITIVE: case_sensitive,
        }
        context_url: str = urllib.parse.quote_plus(context)
        concept_url: str = urllib.parse.quote_plus(reference.iri)
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.CONCEPTS_ENDPOINT}/{concept_url}/metadata"
        )
        response: Response = self.request_session.put(
            url,
            overwrite_auth_token=auth_key,
            json=payload,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if not response.ok:
            raise handle_error("Failed to set concept metadata", response, payload=payload)

    def delete_concept(
        self,
        context: str,
        reference: OntologyClassReference,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Delete concept class.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyClassReference
            Name of the concept
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, exception is thrown.
        """
        context_url: str = urllib.parse.quote_plus(context)
        concept_url: str = urllib.parse.quote_plus(reference.iri)
        url: str = f"{self.service_base_url}context/{context_url}/concepts/{concept_url}"
        response: Response = self.request_session.delete(
            url,
            overwrite_auth_token=auth_key,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if not response.ok:
            raise handle_error("Failed to delete concept", response)

    def create_object_property(
        self,
        context: str,
        reference: OntologyPropertyReference,
        domains_cls: List[OntologyClassReference],
        ranges_cls: List[OntologyClassReference],
        inverse_of: Optional[OntologyPropertyReference] = None,
        subproperty_of: Optional[OntologyPropertyReference] = None,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """Create property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domains_cls: List[OntologyClassReference]
            IRI of the domain
        ranges_cls: List[OntologyClassReference]
            IRI of the range
        inverse_of: Optional[OntologyPropertyReference] (default:= None)
            Inverse property
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)


        Returns
        -------
        result: Dict[str, Any]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        payload: Dict[str, Any] = {
            KIND_TAG: PropertyType.OBJECT_PROPERTY.value,
            DOMAIN_TAG: [d.iri for d in domains_cls],
            RANGE_TAG: [r.iri for r in ranges_cls],
            SUB_PROPERTY_OF_TAG: subproperty_of.iri if subproperty_of is not None else None,
            INVERSE_OF_TAG: inverse_of.iri if inverse_of is not None else None,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        context_url: str = urllib.parse.quote_plus(context)
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.PROPERTIES_ENDPOINT}"
        )

        response: Response = self.request_session.post(
            url,
            json=payload,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return cast(Dict[str, Any], response.json())
        raise handle_error("Failed to create object property", response, payload=payload)

    def create_data_property(
        self,
        context: str,
        reference: OntologyPropertyReference,
        domains_cls: List[OntologyClassReference],
        ranges_cls: List[DataPropertyType],
        subproperty_of: Optional[OntologyPropertyReference] = None,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """Create a data property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the concept
        domains_cls: List[OntologyClassReference]
            IRI of the domain
        ranges_cls: List[DataPropertyType]
            Data property type
        subproperty_of: Optional[OntologyPropertyReference] = None,
            Super property of the concept
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[Label]] (default:= None)
            Labels for the class
        comments: Optional[List[Comment]] (default:= None)
            Comments for the class
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        result: Dict[str, Any]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        payload: Dict[str, Any] = {
            KIND_TAG: PropertyType.DATA_PROPERTY.value,
            DOMAIN_TAG: [d.iri for d in domains_cls],
            RANGE_TAG: [r.value for r in ranges_cls],
            SUB_PROPERTY_OF_TAG: subproperty_of.iri if subproperty_of is not None else None,
            NAME_TAG: reference.iri,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        context_url: str = urllib.parse.quote_plus(context)
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.PROPERTIES_ENDPOINT}"
        )

        response: Response = self.request_session.post(
            url,
            json=payload,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return cast(Dict[str, Any], response.json())
        raise handle_error("Failed to create data property", response, payload=payload)

    def update_property(
        self,
        context: str,
        reference: OntologyPropertyReference,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Update the labels, comments and icon of a property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Domains and ranges are not changed by this call; use `add_property_domains`,
        `remove_property_domains`, `add_property_ranges` and `remove_property_ranges`.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Reference of the property to update
        icon: Optional[str] (default:= None)
            Icon representing the property
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the property
        comments: Optional[List[Comment]] (default:= None)
            Comments for the property
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        payload: Dict[str, Any] = {
            LABELS_TAG: [{TEXT_TAG: la.content, LANGUAGE_CODE: la.language_code} for la in labels or []],
            COMMENTS_TAG: [{TEXT_TAG: co.content, LANGUAGE_CODE: co.language_code} for co in comments or []],
            ICON_TAG: icon,
        }
        context_url: str = urllib.parse.quote_plus(context)
        property_url: str = urllib.parse.quote_plus(reference.iri)
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.PROPERTIES_ENDPOINT}/{property_url}"
        )
        response: Response = self.request_session.patch(
            url,
            overwrite_auth_token=auth_key,
            json=payload,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if not response.ok:
            raise handle_error("Failed to update property", response, payload=payload)

    def rename_property(
        self,
        context: str,
        reference: OntologyPropertyReference,
        new_reference: OntologyPropertyReference,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Rename a property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Current reference of the property
        new_reference: OntologyPropertyReference
            New reference of the property
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        context_url: str = urllib.parse.quote_plus(context)
        property_url: str = urllib.parse.quote_plus(reference.iri)
        new_property_url: str = urllib.parse.quote_plus(new_reference.iri)
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.PROPERTIES_ENDPOINT}/{property_url}/rename/{new_property_url}"
        )
        response: Response = self.request_session.post(
            url,
            overwrite_auth_token=auth_key,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if not response.ok:
            raise handle_error("Failed to rename property", response)

    def _patch_property_collection(
        self,
        context: str,
        reference: OntologyPropertyReference,
        collection: str,
        operation: str,
        iris: List[str],
        error_message: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Send a PATCH to a property's domain or range collection.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Reference of the property
        collection: str
            Either 'domains' or 'ranges'
        operation: str
            Either 'add' or 'remove'
        iris: List[str]
            IRIs to add or remove
        error_message: str
            Message used when the service reports an error
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        context_url: str = urllib.parse.quote_plus(context)
        property_url: str = urllib.parse.quote_plus(reference.iri)
        url: str = (
            f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/"
            f"{OntologyService.PROPERTIES_ENDPOINT}/{property_url}/{collection}/{operation}"
        )
        response: Response = self.request_session.patch(
            url,
            overwrite_auth_token=auth_key,
            json=iris,
            verify=self.verify_calls,
            timeout=timeout,
        )
        if not response.ok:
            raise handle_error(error_message, response)

    def add_property_domains(
        self,
        context: str,
        reference: OntologyPropertyReference,
        domains: List[OntologyClassReference],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Add domains to a property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Reference of the property
        domains: List[OntologyClassReference]
            Classes to add to the property's domain
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        self._patch_property_collection(
            context,
            reference,
            "domains",
            "add",
            [d.iri for d in domains],
            "Failed to add property domains",
            auth_key=auth_key,
            timeout=timeout,
        )

    def remove_property_domains(
        self,
        context: str,
        reference: OntologyPropertyReference,
        domains: List[OntologyClassReference],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Remove domains from a property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Reference of the property
        domains: List[OntologyClassReference]
            Classes to remove from the property's domain
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        self._patch_property_collection(
            context,
            reference,
            "domains",
            "remove",
            [d.iri for d in domains],
            "Failed to remove property domains",
            auth_key=auth_key,
            timeout=timeout,
        )

    def add_property_ranges(
        self,
        context: str,
        reference: OntologyPropertyReference,
        ranges: List[Union[OntologyClassReference, DataPropertyType]],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Add ranges to a property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Reference of the property
        ranges: List[Union[OntologyClassReference, DataPropertyType]]
            Classes (object properties) or data types (data properties) to add
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        self._patch_property_collection(
            context,
            reference,
            "ranges",
            "add",
            [_resolve_range_iri(r) for r in ranges],
            "Failed to add property ranges",
            auth_key=auth_key,
            timeout=timeout,
        )

    def remove_property_ranges(
        self,
        context: str,
        reference: OntologyPropertyReference,
        ranges: List[Union[OntologyClassReference, DataPropertyType]],
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Remove ranges from a property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Reference of the property
        ranges: List[Union[OntologyClassReference, DataPropertyType]]
            Classes (object properties) or data types (data properties) to remove
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        self._patch_property_collection(
            context,
            reference,
            "ranges",
            "remove",
            [_resolve_range_iri(r) for r in ranges],
            "Failed to remove property ranges",
            auth_key=auth_key,
            timeout=timeout,
        )

    def delete_property(
        self,
        context: str,
        reference: OntologyPropertyReference,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Delete property.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Context of ontology
        reference: OntologyPropertyReference
            Name of the property
        auth_key: Optional[str] [default:= None]
            If auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        context_url: str = urllib.parse.quote_plus(context)
        property_url: str = urllib.parse.quote_plus(reference.iri)
        url: str = f"{self.service_base_url}context/{context_url}/properties/{property_url}"
        response: Response = self.request_session.delete(
            url,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if not response.ok:
            raise handle_error("Failed to delete property", response)

    def create_context(
        self,
        name: str,
        context: Optional[str] = None,
        base_uri: Optional[str] = None,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """Create context.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        base_uri: str
            Base URI
        name: str
            Name of the context.
        context: Optional[str] [default:= None]
            Context of ontology
        icon: Optional[str] (default:= None)
            Icon representing the concept
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the context
        comments: Optional[List[Comment]] (default:= None)
            Comments for the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
                timeout: int
            Timeout for the request (default: 60 seconds)
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        result: Dict[str, Any]
            Result from the service

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        if base_uri is None:
            base_uri = f"wacom:{name}#"
        if not base_uri.endswith("#"):
            base_uri += "#"

        payload: Dict[str, Any] = {
            BASE_URI_TAG: base_uri,
            NAME_TAG: name,
            LABELS_TAG: [],
            COMMENTS_TAG: [],
            ICON_TAG: icon,
        }
        if context is not None:
            payload[CONTEXT_TAG] = context
        for label in labels if labels is not None else []:
            payload[LABELS_TAG].append({TEXT_TAG: label.content, LANGUAGE_CODE: label.language_code})
        for comment in comments if comments is not None else []:
            payload[COMMENTS_TAG].append({TEXT_TAG: comment.content, LANGUAGE_CODE: comment.language_code})
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}"
        response: Response = self.request_session.post(
            url,
            json=payload,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return cast(Dict[str, Any], response.json())
        raise handle_error("Creation of context failed.", response)

    def update_context(
        self,
        name: str,
        context: Optional[str] = None,
        base_uri: Optional[str] = None,
        icon: Optional[str] = None,
        labels: Optional[List[OntologyLabel]] = None,
        comments: Optional[List[Comment]] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Update a context.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        name: str
            Name of the context.
        context: Optional[str] [default:= None]
            Context of ontology
        base_uri: Optional[str] [default:= None]
            Base URI. If None, 'wacom:<name>#' is used.
        icon: Optional[str] (default:= None)
            Icon representing the context
        labels: Optional[List[OntologyLabel]] (default:= None)
            Labels for the context
        comments: Optional[List[Comment]] (default:= None)
            Comments for the context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        if base_uri is None:
            base_uri = f"wacom:{name}#"
        if not base_uri.endswith("#"):
            base_uri += "#"

        payload: Dict[str, Any] = {
            BASE_URI_TAG: base_uri,
            NAME_TAG: name,
            LABELS_TAG: [{TEXT_TAG: la.content, LANGUAGE_CODE: la.language_code} for la in labels or []],
            COMMENTS_TAG: [{TEXT_TAG: co.content, LANGUAGE_CODE: co.language_code} for co in comments or []],
            ICON_TAG: icon,
        }
        if context is not None:
            payload[CONTEXT_TAG] = context
        context_url: str = urllib.parse.quote_plus(name)
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}"
        response: Response = self.request_session.put(
            url,
            json=payload,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if not response.ok:
            raise handle_error("Update of context failed.", response, payload=payload)

    def reset_context(
        self,
        name: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Reset a context, discarding its uncommitted changes.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        name: str
            Name of the context.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        context_url: str = urllib.parse.quote_plus(name)
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/reset"
        response: Response = self.request_session.post(
            url,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if not response.ok:
            raise handle_error("Reset of context failed.", response)

    def context_diff(
        self,
        name: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """Retrieve the difference between the committed and the working state of a context.

        **Remark:**
        The OpenAPI specification of the ontology service does not define a response schema
        for this operation, so the parsed JSON payload is returned unmodified.

        Parameters
        ----------
        name: str
            Name of the context.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Returns
        -------
        diff: Dict[str, Any]
            Difference report as returned by the service.

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        context_url: str = urllib.parse.quote_plus(name)
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/diff"
        response: Response = self.request_session.get(
            url,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return cast(Dict[str, Any], response.json())
        raise handle_error("Retrieving the context diff failed.", response)

    def remove_context(
        self,
        name: str,
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Remove context.

        Parameters
        ----------
        name: str
            Name of the context
        force: bool (default:= False)
            Force removal of context
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Raises
        ------
        WacomServiceException
            Raised if the ontology service returns an error code.
        """
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{name}{'/force' if force else ''}"

        response: Response = self.request_session.delete(
            url,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if not response.ok:
            raise handle_error("Removing the context failed.", response)

    def commit(
        self,
        context: str,
        force: bool = False,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Commit the ontology.

        Parameters
        ----------
        context: str
            Name of the context.
        force: bool (default:= False)
            Force commit of the ontology.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)
        """
        context_url: str = urllib.parse.quote_plus(context)
        url: str = f"{self.service_base_url}context/{context_url}/commit"
        params: Dict[str, bool] = {FORCE_TAG: force}
        response: Response = self.request_session.put(
            url,
            params=params,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if not response.ok:
            raise handle_error("Commit of ontology failed.", response)

    def versions(
        self,
        context: str,
        start_at: Optional[int] = None,
        end_at: Optional[int] = None,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> List[Dict[str, Any]]:
        """List the versions of a context.

        **Remark:**
        The OpenAPI specification of the ontology service does not define a response schema
        for this operation, so the parsed JSON payload is returned unmodified.

        Parameters
        ----------
        context: str
            Name of the context.
        start_at: Optional[int] [default:= None]
            First version to list. If None, the service default is used.
        end_at: Optional[int] [default:= None]
            Last version to list. If None, the service default is used.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Returns
        -------
        versions: List[Dict[str, Any]]
            Versions as returned by the service.

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        params: Dict[str, int] = {}
        if start_at is not None:
            params[START_AT_PARAM] = start_at
        if end_at is not None:
            params[END_AT_PARAM] = end_at
        context_url: str = urllib.parse.quote_plus(context)
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/versions"
        response: Response = self.request_session.get(
            url,
            params=params,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return cast(List[Dict[str, Any]], response.json())
        raise handle_error("Failed to retrieve versions", response)

    def pending_version(
        self,
        context: str,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """Retrieve the pending, uncommitted version of a context.

        **Remark:**
        The OpenAPI specification of the ontology service does not define a response schema
        for this operation, so the parsed JSON payload is returned unmodified.

        Parameters
        ----------
        context: str
            Name of the context.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Returns
        -------
        pending: Dict[str, Any]
            Pending version as returned by the service.

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        context_url: str = urllib.parse.quote_plus(context)
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/versions/pending"
        response: Response = self.request_session.get(
            url,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return cast(Dict[str, Any], response.json())
        raise handle_error("Failed to retrieve the pending version", response)

    def rdf_export(
        self,
        context: str,
        version: int = 0,
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> str:
        """
        Export RDF.

        Parameters
        ----------
        context: str
            Name of the context.
        version: int (default:= 0)
            Version of the context if 0 is set, the latest version will be exported.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 60 seconds)

        Returns
        -------
        rdf: str
            Ontology as RDFS / OWL ontology
        """
        params: Dict[str, int]
        if version > 0:
            params = {"version": version}
        else:
            params = {}
        context_url: str = urllib.parse.quote_plus(context)
        url: str = f"{self.service_base_url}context/{context_url}/versions/rdf"
        response: Response = self.request_session.get(
            url,
            verify=self.verify_calls,
            params=params,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return str(response.text)
        raise handle_error("RDF export failed", response)

    def rdf_import(
        self,
        context: str,
        rdf_content: Union[str, bytes],
        file_name: str = "ontology.rdf",
        auth_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> ImportResponse:
        """Import an RDF ontology file into a context.

        **Remark:**
        Only works for users with the role 'TenantAdmin'.

        Parameters
        ----------
        context: str
            Name of the context.
        rdf_content: Union[str, bytes]
            RDFS / OWL ontology content. Strings are encoded as UTF-8.
        file_name: str (default:= 'ontology.rdf')
            File name transmitted with the multipart upload.
        auth_key: Optional[str] [default:= None]
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.
        timeout: int
            Timeout for the request (default: 30 seconds)

        Returns
        -------
        result: ImportResponse
            Import outcome for concepts and properties.

        Raises
        ------
        WacomServiceException
            If the ontology service returns an error code, an exception is thrown.
        """
        content: bytes = rdf_content.encode("utf-8") if isinstance(rdf_content, str) else rdf_content
        context_url: str = urllib.parse.quote_plus(context)
        url: str = f"{self.service_base_url}{OntologyService.CONTEXT_ENDPOINT}/{context_url}/versions/rdf"
        response: Response = self.request_session.post(
            url,
            files={"file": (file_name, content)},
            ignore_content_type=True,
            verify=self.verify_calls,
            timeout=timeout,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            return ImportResponse.from_dict(response.json())
        raise handle_error("RDF import failed", response)
