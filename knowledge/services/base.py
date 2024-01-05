# -*- coding: utf-8 -*-
# Copyright © 2021-24 Wacom. All rights reserved.
from abc import ABC
from datetime import timezone, datetime
from typing import Any, Tuple, Dict, Optional

import jwt
import requests
from dateutil.parser import parse, ParserError
from requests import Response

from knowledge.services import USER_AGENT_STR, USER_AGENT_HEADER_FLAG, TENANT_API_KEY, CONTENT_TYPE_HEADER_FLAG, \
    REFRESH_TOKEN_TAG, EXPIRATION_DATE_TAG, ACCESS_TOKEN_TAG, APPLICATION_JSON_HEADER, EXTERNAL_USER_ID
from knowledge.services import DEFAULT_TIMEOUT


class WacomServiceException(Exception):
    """Exception thrown if Wacom service fails."""
    def __init__(self, message: str, headers: Optional[Dict[str, Any]] = None, payload: Optional[Dict[str, Any]] = None,
                 params: Optional[Dict[str, Any]] = None, method: Optional[str] = None,
                 url: Optional[str] = None,  service_response: Optional[str] = None,  status_code: int = 500):
        super().__init__(message)
        self.__status_code: int = status_code
        self.__service_response: Optional[str] = service_response
        self.__message: str = message
        self.__headers: Optional[Dict[str, Any]] = headers
        self.__payload: Optional[Dict[str, Any]] = payload
        self.__params: Optional[Dict[str, Any]] = params
        self.__method: Optional[str] = method
        self.__url: Optional[str] = url

    @property
    def headers(self) -> Optional[Dict[str, Any]]:
        """Headers of the exception."""
        return self.__headers

    @property
    def method(self) -> Optional[str]:
        """Method of the exception."""
        return self.__method

    @property
    def params(self) -> Optional[Dict[str, Any]]:
        """Parameters of the exception."""
        return self.__params

    @property
    def payload(self) -> Optional[Dict[str, Any]]:
        """Payload of the exception."""
        return self.__payload

    @property
    def url(self) -> Optional[str]:
        """URL of the exception."""
        return self.__url

    @property
    def message(self) -> str:
        """Message of the exception."""
        return self.__message

    @property
    def service_response(self) -> Optional[Response]:
        """Service response."""
        return self.__service_response

    @property
    def status_code(self) -> int:
        """Status code of the exception."""
        return self.__status_code


def handle_error(message: str, response: Response, parameters: Optional[Dict[str, Any]] = None,
                 payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
    """
    Handles an error response.

    Parameters
    ----------
    message: str
        Error message
    response: aiohttp.ClientResponse
        Response
    parameters: Optional[Dict[str, Any]] (Default:= None)
        Parameters
    payload: Optional[Dict[str, Any]] (Default:= None)
        Payload
    headers: Optional[Dict[str, str]] (Default:= None)
        Headers

    Raises
    ------
    WacomServiceException
        Exception if service returns HTTP error code.
    """
    raise WacomServiceException(message,
                                url=response.url,
                                method=response.request.method,
                                params=parameters,
                                payload=payload,
                                headers=headers,
                                status_code=response.status_code,
                                service_response=response.text)


class RESTAPIClient(ABC):
    """
    Abstract REST API client
    ------------------------
    REST API client handling the service url.

    Arguments
    ---------
    service_url: str
        Service URL for service
    verify_calls: bool (default:= False)
        Flag if the service calls should be verified
    """
    def __init__(self, service_url: str, verify_calls: bool = False):
        self.__service_url: str = service_url.rstrip('/')
        self.__verify_calls: bool = verify_calls

    @property
    def service_url(self) -> str:
        """Service URL."""
        return self.__service_url

    @property
    def verify_calls(self):
        """Certificate verification activated."""
        return self.__verify_calls

    @verify_calls.setter
    def verify_calls(self, value: bool):
        self.__verify_calls = value


class WacomServiceAPIClient(RESTAPIClient):
    """
    Wacom Service API Client
    ------------------------
    Abstract class for Wacom service APIs.

    Parameters
    ----------
    application_name: str
        Name of the application using the service
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    auth_service_endpoint: str (Default:= 'graph/v1')
        Authentication service endpoint
    verify_calls: bool (Default:= True)
        Flag if  API calls should be verified.
    """
    USER_ENDPOINT: str = 'user'
    USER_LOGIN_ENDPOINT: str = f'{USER_ENDPOINT}/login'
    USER_REFRESH_ENDPOINT: str = f'{USER_ENDPOINT}/refresh'
    SERVICE_URL: str = 'https://private-knowledge.wacom.com'
    """Production service URL"""
    STAGING_SERVICE_URL: str = 'https://stage-private-knowledge.wacom.com'
    """Staging service URL"""

    def __init__(self, application_name: str, service_url: str, service_endpoint: str,
                 auth_service_endpoint: str = 'graph/v1', verify_calls: bool = True):
        self.__auth_key: Optional[str] = None
        self.__refresh_token: Optional[str] = None
        self.__application_name: str = application_name
        self.__service_endpoint: str = service_endpoint
        self.__auth_service_endpoint: str = auth_service_endpoint
        super().__init__(service_url, verify_calls)

    @property
    def auth_endpoint(self) -> str:
        """Authentication endpoint."""
        # This is in graph service REST API
        return f'{self.service_url}/{self.__auth_service_endpoint}/{self.USER_LOGIN_ENDPOINT}'

    def request_user_token(self, tenant_key: str, external_id: str) -> Tuple[str, str, datetime]:
        """
        Login as user by using the tenant key and its external user id.

        Parameters
        ----------
        tenant_key: str
            Tenant key
        external_id: str
            External id.

        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_key: str
            Refresh token
        expiration_time: datatime
            Expiration time

        Raises
        ------
        WacomServiceException
            Exception if service returns HTTP error code.
        """
        url: str = f'{self.auth_endpoint}'
        headers: dict = {
            USER_AGENT_HEADER_FLAG: USER_AGENT_STR,
            TENANT_API_KEY: tenant_key,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER
        }
        payload: dict = {
            EXTERNAL_USER_ID: external_id
        }
        response: Response = requests.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT,
                                           verify=self.verify_calls)
        if response.ok:
            try:
                response_token: Dict[str, str] = response.json()
                try:
                    date_object: datetime = parse(response_token['expirationDate'])
                except (ParserError, OverflowError) as _:
                    date_object: datetime = datetime.now()
                return response_token['accessToken'], response_token['refreshToken'], date_object
            except Exception as e:
                handle_error(f'Parsing of response failed. {e}', response)
        handle_error(f'User login failed.', response)

    def login(self, tenant_id: str, external_user_id: str):
        """ Login as user by using the tenant id and its external user id.
        Parameters
        ----------
        tenant_id: str
            Tenant id
        external_user_id: str
            External user id
        """
        auth_key, refresh_token, exp = self.request_user_token(tenant_id, external_user_id)
        self.__auth_key = auth_key
        self.__refresh_token = refresh_token

    def logout(self):
        """ Logout user."""
        self.__auth_key = None
        self.__refresh_token = None

    def register_token(self, auth_key: str, refresh_token: Optional[str] = None):
        """ Register token.
        Parameters
        ----------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_token: str
            Refresh token
        """
        self.__auth_key = auth_key
        self.__refresh_token = refresh_token

    def refresh_token(self, refresh_token: str) -> Tuple[str, str, datetime]:
        """
        Refreshing a token.

        Parameters
        ----------
        refresh_token: str
            Refresh token

        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_key: str
            Refresh token
        expiration_time: str
            Expiration time

        Raises
        ------
        WacomServiceException
            Exception if service returns HTTP error code.
        """
        url: str = f'{self.service_base_url}/{WacomServiceAPIClient.USER_REFRESH_ENDPOINT}/'
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: USER_AGENT_STR,
            CONTENT_TYPE_HEADER_FLAG: 'application/json'
        }
        payload: Dict[str, str] = {
            REFRESH_TOKEN_TAG: refresh_token
        }
        response: Response = requests.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT,
                                           verify=self.verify_calls)
        if response.ok:
            response_token: Dict[str, str] = response.json()
            try:
                date_object: datetime = parse(response_token[EXPIRATION_DATE_TAG])
            except (ParserError, OverflowError) as _:
                date_object: datetime = datetime.now()
            return response_token[ACCESS_TOKEN_TAG], response_token[REFRESH_TOKEN_TAG], date_object
        handle_error(f'Refreshing token failed.', response)

    def handle_token(self, force_refresh: bool = False, force_refresh_timeout: float = 120) -> Tuple[str, str]:
        """
        Handles the token and refreshes it if needed.

        Parameters
        ----------
        force_refresh: bool
            Force refresh token
        force_refresh_timeout: int
            Force refresh timeout
        Returns
        -------
        user_token: str
            The user token
        refresh_token: str
            The refresh token
        """
        if self.__auth_key is None:
            raise WacomServiceException('Authentication key is not set. Please login first.')
        # Refresh token if needed
        if WacomServiceAPIClient.expires_in(self.__auth_key) < force_refresh_timeout or force_refresh:
            if self.__refresh_token is None:
                raise WacomServiceException('Refresh token is not set. Please login first.')
            self.__auth_key, self.__refresh_token, _ = self.refresh_token(self.__refresh_token)
        return self.__auth_key, self.__refresh_token

    @staticmethod
    def unpack_token(auth_token: str) -> Dict[str, Any]:
        """Unpacks the token.

        Parameters
        ----------
        auth_token: str
            Authentication token

        Returns
        -------
        token_dict: Dict[str, Any]
            Token dictionary
        """
        return jwt.decode(auth_token, options={"verify_signature": False})

    @staticmethod
    def expired(auth_token: str) -> bool:
        """
        Checks if token is expired.

        Parameters
        ----------
        auth_token: str
            Authentication token

        Returns
        -------
        expired: bool
            Flag if token is expired
        """
        return WacomServiceAPIClient.expires_in(auth_token) > 0.

    @staticmethod
    def expires_in(auth_token: str) -> float:
        """
        Returns the seconds when the token expires.

        Parameters
        ----------
        auth_token: str
            Authentication token

        Returns
        -------
        expired_in: float
            Seconds until token is expired
        """
        token_dict: Dict[str, Any] = WacomServiceAPIClient.unpack_token(auth_token)
        timestamp: datetime = datetime.now(tz=timezone.utc)
        expiration_time: datetime = datetime.fromtimestamp(token_dict['exp'], tz=timezone.utc)
        return expiration_time.timestamp() - timestamp.timestamp()

    @property
    def service_endpoint(self):
        """Service endpoint."""
        return '' if len(self.__service_endpoint) == 0 else f'{self.__service_endpoint}/'

    @property
    def service_base_url(self):
        """Service endpoint."""
        return f'{self.service_url}/{self.service_endpoint}'

    @property
    def application_name(self):
        """Application name."""
        return self.__application_name
