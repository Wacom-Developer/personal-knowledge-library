# -*- coding: utf-8 -*-
# Copyright © 2021-23 Wacom. All rights reserved.
from abc import ABC
from datetime import timezone, datetime
from typing import Any, Tuple, Dict

import jwt
import requests
from dateutil.parser import parse, ParserError
from requests import Response

from knowledge.services import USER_AGENT_STR

# Constants for header tags
USER_AGENT_HEADER_FLAG: str = 'User-Agent'
AUTHORIZATION_HEADER_FLAG: str = 'Authorization'
CONTENT_TYPE_HEADER_FLAG: str = 'Content-Type'
TENANT_API_KEY: str = 'x-tenant-api-key'
REFRESH_TOKEN_TAG: str = 'refreshToken'
EXPIRATION_DATE_TAG: str = 'expirationDate'
ACCESS_TOKEN_TAG: str = 'accessToken'
DEFAULT_TIMEOUT: int = 60


class WacomServiceException(Exception):
    """Exception thrown if Wacom service fails."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.__status_code: int = status_code

    @property
    def status_code(self) -> int:
        """Status code of the exception."""
        return self.__status_code


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
        self.__service_url: str = service_url
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
    verify_calls: bool (Default:= False)
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
            CONTENT_TYPE_HEADER_FLAG: 'application/json'
        }
        payload: dict = {
            'ExternalUserId': external_id
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
                raise WacomServiceException(f'Login failed'
                                            f'Response code:={response.status_code}, response text:= {response.text}, '
                                            f'exception:= {e} ')
        raise WacomServiceException(f'User login failed.'
                                    f'Response code:={response.status_code}, exception:= {response.text}',
                                    status_code=response.status_code)

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
        raise WacomServiceException(f'Refresh failed. '
                                    f'Response code:={response.status_code}, exception:= {response.text}')

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
