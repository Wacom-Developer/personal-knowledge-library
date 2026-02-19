# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
from typing import Dict, Any, Optional, List

from knowledge.base.queue import QueueMonitor, QueueCount, QueueNames
from knowledge.services import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF_FACTOR,
)
from knowledge.services.base import WacomServiceAPIClient, handle_error

__all__ = ["QueueManagementClient"]


class QueueManagementClient(WacomServiceAPIClient):
    """

    """

    def __init__(
        self,
        service_url: str,
        application_name: str = "Queue Management Client",
        base_auth_url: Optional[str] = None,
        service_endpoint: str = "vector/api/v1",
        verify_calls: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        super().__init__(
            service_url=service_url,
            application_name=application_name,
            base_auth_url=base_auth_url,
            service_endpoint=service_endpoint,
            verify_calls=verify_calls,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    def list_queue_names(self, auth_key: Optional[str] = None) -> QueueNames:
        """
        List all available queues in the semantic search service.

        Parameters
        ----------
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.

        Returns
        -------
        queues: QueueNames
            List of queue names.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}queues/names/"
        response = self.request_session.get(
            url,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            queues: Dict[str, List[str]] = response.json()
            return QueueNames.parse_json(queues)
        raise handle_error(
            "Failed to list queues.",
            response,
        )

    def list_queues(self, auth_key: Optional[str] = None) -> List[QueueMonitor]:
        """

        Parameters
        ----------
        auth_key: Optional[str] (Default:= None)
            If the auth key is set, the logged-in user (if any) will be ignored and the auth key will be used.

        Returns
        -------
        queues: List[QueueMonitor]
            List of queues.

        Raises
        ------
        WacomServiceException
            If the request fails.
        """
        url: str = f"{self.service_base_url}queues/all/"
        response = self.request_session.get(
            url,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            queues: List[Dict[str, Any]] = response.json()
            return [QueueMonitor.parse_json(queue) for queue in queues]
        raise handle_error(
            "Failed to list queues.",
            response,
        )

    def queue_is_empty(self, queue_name: str, auth_key: Optional[str] = None) -> bool:
        """
        Checks if a given queue is empty.

        This asynchronous method checks whether the specified queue exists and if it is
        empty by interacting with a remote service. It uses an authorization key for
        authentication, and if not provided, retrieves it using a helper method.

        Parameters
        ----------
        queue_name : str
            The name of the queue to check.
        auth_key : Optional[str], optional
            Authorization key used for authenticating with the service. Defaults
            to None, in which case the method will fetch an appropriate token.

        Returns
        -------
        bool
            True if the specified queue is empty, False otherwise.
        """
        url: str = f"{self.service_base_url}queues/empty/"
        params: Dict[str, str] = {"queue_name": queue_name}
        response = self.request_session.get(
            url,
            params=params,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            is_empty: bool = response.json()
            return is_empty
        raise handle_error("Failed to check if the queue is empty.", response)

    def queue_size(self, queue_name: str, auth_key: Optional[str] = None) -> QueueCount:
        """
        Gets the size of a specified queue by making an asynchronous request to the service's
        queue management endpoint. The method interacts with a remote API, utilizing prepared
        headers and query parameters, and parses the returned data into the appropriate
        response structure upon a successful response.

        Parameters
        ----------
        queue_name : str
            The name of the queue whose size is being retrieved.
        auth_key : Optional[str], optional
            An optional authentication key to overwrite the default one when preparing headers.

        Returns
        -------
        QueueCount
            The parsed response encapsulating the size and additional metadata of the specified
            queue.

        Raises
        ------
        Exception
            If the API request fails, an error is raised with the relevant information.
        """
        url: str = f"{self.service_base_url}queues/count/"
        params: Dict[str, str] = {"queue_name": queue_name}
        response = self.request_session.get(
            url,
            params=params,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            response_structure: Dict[str, Any] = response.json()
            return QueueCount.parse_json(response_structure)
        raise handle_error("Failed to get the queue size.", response)

    def queue_monitor_information(self, queue_name: str, auth_key: Optional[str] = None) -> QueueMonitor:
        """
        Gets the monitoring information for a specific queue.

        Parameters
        ----------
        queue_name : str
            The name of the queue for which monitoring information is requested.
        auth_key : Optional[str], optional
            An optional authentication key to be used for the request. If not provided,
            an internal token will be fetched and used.

        Returns
        -------
        QueueMonitor
            A parsed representation of the queue monitoring information.

        Raises
        ------
        Exception
            Raised if the request fails or if there is an issue with fetching the
            monitoring data. Details of the failure are included.
        """
        url: str = f"{self.service_base_url}queues/"
        params: Dict[str, str] = {"queue_name": queue_name}
        response = self.request_session.get(
            url,
            params=params,
            overwrite_auth_token=auth_key,
        )
        if response.ok:
            response_structure: Dict[str, Any] = response.json()
            return QueueMonitor.parse_json(response_structure)
        raise handle_error("Failed to get the queue monitor information.", response)
