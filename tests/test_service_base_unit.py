# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the sync transport and token handling in ``knowledge/services/base.py``.

JWTs are minted locally and no request leaves the process — the tests exercise the retry
policy that is configured on the adapter and the concurrency of token refresh.
"""

import threading
import time
from typing import Any, List, Tuple

import jwt
import pytest
import requests

from knowledge.services.base import WacomServiceAPIClient
from knowledge.services.graph import WacomKnowledgeService

SERVICE_URL: str = "https://example.invalid"


def _make_jwt(expires_in: int = 3600) -> str:
    """Mint a JWT for tests."""
    return jwt.encode(
        {
            "tenant": "tenant-a",
            "roles": "user",
            "iss": "https://example.invalid",
            "ext-sub": "user-1",
            "exp": int(time.time()) + expires_in,
        },
        "test-secret",
        algorithm="HS256",
    )


# ------------------------------------------ retry policy --------------------------------------------------------------
def test_the_retry_policy_covers_idempotent_methods() -> None:
    """GET, PUT and DELETE are safe to replay after a transient gateway error."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    session: requests.Session = client.request_session._create_session()

    allowed = session.get_adapter(SERVICE_URL).max_retries.allowed_methods

    assert {"GET", "PUT", "DELETE"} <= set(allowed)


def test_the_retry_policy_does_not_replay_entity_creating_methods() -> None:
    """POST and PATCH must not be retried automatically.

    A 502/503/504 from a gateway can arrive after the backend already committed, so
    replaying ``create_entity`` would silently create a duplicate. Callers decide, using
    the source reference id to check whether the first attempt landed.
    """
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    session: requests.Session = client.request_session._create_session()

    allowed = session.get_adapter(SERVICE_URL).max_retries.allowed_methods

    assert "POST" not in allowed
    assert "PATCH" not in allowed


def test_the_retry_policy_still_targets_transient_gateway_errors() -> None:
    """The status codes that warrant a retry are unchanged."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    session: requests.Session = client.request_session._create_session()

    status_forcelist = session.get_adapter(SERVICE_URL).max_retries.status_forcelist

    assert {502, 503, 504} <= set(status_forcelist)


# --------------------------------------- concurrent token refresh -----------------------------------------------------
def test_a_shared_client_refreshes_its_token_once_under_concurrency(monkeypatch: pytest.MonkeyPatch) -> None:
    """Threads sharing one client must not each fire their own refresh.

    Without a lock every thread sees the same nearly-expired token and posts to
    ``/user/refresh`` simultaneously; if the service rotates refresh tokens, all but one
    of those requests invalidate the token the others are about to use.
    """
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    # A token that is inside the refresh window, so every caller wants to refresh.
    client.register_token(auth_key=_make_jwt(expires_in=30), refresh_token="refresh-token-0")
    refreshes: List[str] = []
    lock: threading.Lock = threading.Lock()

    def counting_refresh(refresh_token: str, timeout: int = 0) -> Tuple[str, str, Any]:
        with lock:
            refreshes.append(refresh_token)
        time.sleep(0.02)  # widen the window a real HTTP round-trip would open
        return _make_jwt(expires_in=3600), f"refresh-token-{len(refreshes)}", None

    monkeypatch.setattr(client, "refresh_token", counting_refresh)
    errors: List[BaseException] = []

    def call_handle_token() -> None:
        try:
            client.handle_token()
        except BaseException as error:  # noqa: BLE001 - surfaced through the assertion below
            errors.append(error)

    threads = [threading.Thread(target=call_handle_token) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert len(refreshes) == 1, f"token was refreshed {len(refreshes)} times by 8 threads"


def test_handle_token_returns_the_current_token_when_it_is_still_fresh() -> None:
    """A token far from expiry is handed back untouched."""
    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)
    token: str = _make_jwt(expires_in=3600)
    client.register_token(auth_key=token, refresh_token="refresh-token")

    auth_token, refresh = client.handle_token()

    assert auth_token == token
    assert refresh == "refresh-token"


def test_handle_token_without_a_session_is_reported() -> None:
    """Calling before login is an error, not a silent empty token."""
    from knowledge.services.base import WacomServiceException

    client: WacomKnowledgeService = WacomKnowledgeService(service_url=SERVICE_URL)

    with pytest.raises(WacomServiceException):
        client.handle_token()


def test_the_client_is_still_constructible_without_a_session() -> None:
    """Guard against the retry/lock changes breaking plain construction."""
    client: WacomServiceAPIClient = WacomServiceAPIClient(service_url=SERVICE_URL)

    assert client.service_url == SERVICE_URL
