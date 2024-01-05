# -*- coding: utf-8 -*-
# Copyright © 2021-23 Wacom. All rights reserved.
import asyncio
import json
import logging
import socket
import ssl
from datetime import timezone, datetime
from typing import Any, Tuple, Dict, Optional

import aiohttp
import jwt
import orjson
from aiohttp import ClientTimeout
from cachetools import TTLCache
from dateutil.parser import parse, ParserError

from knowledge.services import USER_AGENT_STR, DEFAULT_TOKEN_REFRESH_TIME, USER_AGENT_HEADER_FLAG, TENANT_API_KEY, \
    CONTENT_TYPE_HEADER_FLAG, REFRESH_TOKEN_TAG, DEFAULT_TIMEOUT, EXPIRATION_DATE_TAG, ACCESS_TOKEN_TAG, \
    APPLICATION_JSON_HEADER, EXTERNAL_USER_ID
from knowledge.services.base import WacomServiceException, RESTAPIClient


# A cache for storing DNS resolutions
dns_cache: TTLCache = TTLCache(maxsize=100, ttl=300)  # Adjust size and ttl as needed


async def cached_getaddrinfo(host: str, *args, **kwargs) -> Any:
    """
    Cached address information.

    Parameters
    ----------
    host: str
        Hostname
    args: Any
        Additional arguments
    kwargs: Any
        Additional keyword arguments

    Returns
    -------
    addr_info: Any
        Address information
    """
    if host in dns_cache:
        return dns_cache[host]
    addr_info = await asyncio.get_running_loop().getaddrinfo(host, port=None, *args, **kwargs)
    dns_cache[host] = addr_info
    return addr_info


class CachedResolver(aiohttp.resolver.AbstractResolver):
    """
    CachedResolver
    ==============
    Cached resolver for aiohttp.
    """

    async def close(self) -> None:
        pass

    async def resolve(self, host: str, port: int = 0, family: int = socket.AF_INET):
        infos = await cached_getaddrinfo(host)
        return [{'hostname': host, 'host': info[4][0], 'port': port, 'family': family, 'proto': 0,
                 'flags': socket.AI_NUMERICHOST} for info in infos]


cached_resolver: CachedResolver = CachedResolver()
""" Cached resolver for aiohttp."""


async def handle_error(message: str, response: aiohttp.ClientResponse, parameters: Optional[Dict[str, Any]] = None,
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
    try:
        response_text: str = await response.text()
    except Exception as e:
        logging.error(f'Error while reading response text: {e}')
        response_text: str = ""
    raise WacomServiceException(message,
                                method=response.method,
                                url=response.url.human_repr(),
                                params=parameters,
                                payload=payload,
                                headers=headers,
                                status_code=response.status,
                                service_response=response_text)


class AsyncServiceAPIClient(RESTAPIClient):
    """
    Async Wacom Service API Client
    ------------------------------
    Abstract class for Wacom service APIs.

    Parameters
    ----------
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

    def __init__(self, service_url: str, service_endpoint: str,
                 auth_service_endpoint: str = 'graph/v1', verify_calls: bool = True):
        self.__service_endpoint: str = service_endpoint
        self.__auth_service_endpoint: str = auth_service_endpoint
        self.__auth_key: Optional[str] = None
        self.__refresh_token: Optional[str] = None
        super().__init__(service_url, verify_calls)

    @property
    def auth_endpoint(self) -> str:
        """Authentication endpoint."""
        # This is in graph service REST API
        return f'{self.service_url}/{self.__auth_service_endpoint}/{self.USER_LOGIN_ENDPOINT}'

    async def handle_token(self, force_refresh: bool = False, refresh_time: float = DEFAULT_TOKEN_REFRESH_TIME) \
            -> Tuple[str, str]:
        """
        Handles the token and refreshes it if needed.

        Parameters
        ----------
        force_refresh: bool (Default:= False)
            Flag if token should be refreshed.
        refresh_time: float (Default:= DEFAULT_TOKEN_REFRESH_TIME)
            Refresh time in seconds. Default is 360 seconds = 6 minutes

        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.
        refresh_key: str
            Refresh token

        Raises
        ------
        WacomServiceException
            Exception if service returns HTTP error code.
        """
        if self.__auth_key is None:
            raise WacomServiceException('Authentication key is not set. Please login first.')
        # Refresh token if needed
        expires_in: float = await self.expires_in(self.__auth_key)
        if expires_in < refresh_time or force_refresh:
            if self.__refresh_token is None:
                raise WacomServiceException('Refresh token is not set. Please login first.')
            self.__auth_key, self.__refresh_token, expr = await self.refresh_token(self.__refresh_token)
        return self.__auth_key, self.__refresh_token

    @staticmethod
    def __async_session__() -> aiohttp.ClientSession:
        """
        Returns an asynchronous session.

        Returns
        -------
        session: aiohttp.ClientSession
            Asynchronous session
        """
        global cached_resolver
        timeout: ClientTimeout = ClientTimeout(total=60)
        ssl_context: ssl.SSLContext = ssl.create_default_context()
        connector: aiohttp.TCPConnector = aiohttp.TCPConnector(ssl_context=ssl_context, limit_per_host=10,
                                                               resolver=cached_resolver)
        return aiohttp.ClientSession(
            json_serialize=lambda x: orjson.dumps(x).decode(),
            timeout=timeout,
            connector=connector
        )

    async def request_user_token(self, tenant_key: str, external_id: str) -> Tuple[str, str, datetime]:
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
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: USER_AGENT_STR,
            TENANT_API_KEY: tenant_key,
            CONTENT_TYPE_HEADER_FLAG: APPLICATION_JSON_HEADER
        }
        payload: dict = {
            EXTERNAL_USER_ID: external_id
        }
        async with AsyncServiceAPIClient.__async_session__() as session:
            async with session.post(self.auth_endpoint, data=json.dumps(payload), headers=headers) as response:
                if response.ok:
                    response_token: Dict[str, str] = await response.json(loads=orjson.loads)
                    try:
                        date_object: datetime = parse(response_token['expirationDate'])
                    except (ParserError, OverflowError) as _:
                        date_object: datetime = datetime.now()
                    return response_token['accessToken'], response_token['refreshToken'], date_object
                raise WacomServiceException(f'Login failed'
                                            f'Response code:={response.status}, '
                                            f'response text:= {await response.text()}')

    async def refresh_token(self, refresh_token: str) -> Tuple[str, str, datetime]:
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
        url: str = f'{self.service_base_url}/{AsyncServiceAPIClient.USER_REFRESH_ENDPOINT}/'
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG: USER_AGENT_STR,
            CONTENT_TYPE_HEADER_FLAG: 'application/json'
        }
        payload: Dict[str, str] = {
            REFRESH_TOKEN_TAG: refresh_token
        }
        async with self.__async_session__() as session:
            async with session.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT,
                                    verify=self.verify_calls) as response:
                if response.ok:
                    response_token: Dict[str, str] = await response.json()
                    try:
                        date_object: datetime = parse(response_token[EXPIRATION_DATE_TAG])
                    except (ParserError, OverflowError) as _:
                        date_object: datetime = datetime.now()
                    return response_token[ACCESS_TOKEN_TAG], response_token[REFRESH_TOKEN_TAG], date_object
        raise WacomServiceException(f'Refresh failed. '
                                    f'Response code:={response.status}, exception:= {response.text}')

    async def login(self, tenant_key: str, external_user_id: str):
        """ Login as user by using the tenant id and its external user id.
        Parameters
        ----------
        tenant_key: str
            Tenant id
        external_user_id: str
            External user id
        """
        auth_key, refresh_token, exp = await self.request_user_token(tenant_key, external_user_id)
        self.__auth_key = auth_key
        self.__refresh_token = refresh_token

    async def logout(self):
        """ Logout user."""
        self.__auth_key = None
        self.__refresh_token = None

    async def register_token(self, auth_key: str, refresh_token: Optional[str] = None):
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

    @staticmethod
    async def unpack_token(auth_token: str) -> Dict[str, Any]:
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
    async def expired(auth_token: str) -> bool:
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
        return await AsyncServiceAPIClient.expires_in(auth_token) > 0.

    @staticmethod
    async def expires_in(auth_token: str) -> float:
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
        token_dict: Dict[str, Any] = await AsyncServiceAPIClient.unpack_token(auth_token)
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

