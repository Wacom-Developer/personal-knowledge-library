# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the async transport in ``knowledge/services/asyncio/base.py``.

Covers the DNS resolver cache and the request keyword arguments handed to aiohttp. No
network: the aiohttp session is replaced by a recorder and ``getaddrinfo`` by a stub.
"""

import socket
from typing import Any, Dict, List, Tuple

import pytest
from aiohttp import ClientTimeout

from knowledge.services.asyncio.base import (
    AsyncSession,
    AsyncServiceAPIClient,
    CachedResolver,
    dns_cache,
)

SERVICE_URL: str = "https://example.invalid"


@pytest.fixture(autouse=True)
def _clear_dns_cache() -> Any:
    dns_cache.clear()
    yield
    dns_cache.clear()


# --------------------------------------------- DNS cache --------------------------------------------------------------
async def test_closing_one_session_keeps_the_dns_cache_of_the_others() -> None:
    """The DNS cache is process-global, so one client closing must not wipe it.

    Clearing it on close throws away resolutions every other live client is still using,
    and the TTL already bounds the cache's lifetime.
    """
    dns_cache["example.invalid"] = [(socket.AF_INET, 0, 0, "", ("10.0.0.1", 0))]
    session: AsyncSession = AsyncSession(client=AsyncServiceAPIClient(service_url=SERVICE_URL))

    await session.close()

    assert "example.invalid" in dns_cache


async def test_the_resolver_reports_the_family_it_was_asked_for() -> None:
    """``resolve`` must honour the family aiohttp passes rather than assuming IPv4."""
    resolver: CachedResolver = CachedResolver()
    recorded: List[Tuple[Any, ...]] = []

    async def fake_getaddrinfo(host: str, *args: Any, **kwargs: Any) -> Any:
        recorded.append((host, args, kwargs))
        return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", 0, 0, 0))]

    import knowledge.services.asyncio.base as base_module

    original = base_module.cached_getaddrinfo
    base_module.cached_getaddrinfo = fake_getaddrinfo  # type: ignore[assignment]
    try:
        infos = await resolver.resolve("example.invalid", 443, family=socket.AF_INET6)
    finally:
        base_module.cached_getaddrinfo = original  # type: ignore[assignment]

    assert infos[0]["family"] == socket.AF_INET6
    assert infos[0]["host"] == "::1"
    assert infos[0]["port"] == 443


async def test_the_dns_cache_distinguishes_address_families() -> None:
    """An IPv4 lookup must not be served from an IPv6 entry for the same host."""
    calls: List[Tuple[str, int]] = []

    async def fake_getaddrinfo(host: str, port: Any, *args: Any, **kwargs: Any) -> Any:
        family = kwargs.get("family", args[0] if args else 0)
        calls.append((host, family))
        return [(family, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 0))]

    import knowledge.services.asyncio.base as base_module

    monkeyed = base_module.asyncio.get_running_loop()
    setattr(monkeyed, "getaddrinfo", fake_getaddrinfo)

    resolver: CachedResolver = CachedResolver()
    await resolver.resolve("example.invalid", 443, family=socket.AF_INET)
    await resolver.resolve("example.invalid", 443, family=socket.AF_INET6)

    assert len(calls) == 2, "the second family was served from the first family's cache entry"


# ------------------------------------------ request keywords ----------------------------------------------------------
class _RecordingResponse:
    def __init__(self) -> None:
        self.ok = True
        self.status = 200
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}
        self.method = "GET"

    @property
    def url(self) -> Any:
        class _Url:
            @staticmethod
            def human_repr() -> str:
                return SERVICE_URL

        return _Url()

    async def read(self) -> bytes:
        return b"{}"

    async def json(self, **kwargs: Any) -> Dict[str, Any]:
        return {}

    async def __aenter__(self) -> "_RecordingResponse":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None


class _RecordingClientSession:
    """Captures the keyword arguments the AsyncSession hands to aiohttp."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.closed = False

    def get(self, **kwargs: Any) -> _RecordingResponse:
        self.calls.append(kwargs)
        return _RecordingResponse()

    def post(self, **kwargs: Any) -> _RecordingResponse:
        self.calls.append(kwargs)
        return _RecordingResponse()

    async def close(self) -> None:
        self.closed = True


@pytest.fixture()
def recording_aiohttp(monkeypatch: pytest.MonkeyPatch) -> _RecordingClientSession:
    aiohttp_session: _RecordingClientSession = _RecordingClientSession()

    async def create_session(self: AsyncSession) -> _RecordingClientSession:
        return aiohttp_session

    monkeypatch.setattr(AsyncSession, "_create_session", create_session)
    return aiohttp_session


def _session() -> AsyncSession:
    return AsyncSession(client=AsyncServiceAPIClient(service_url=SERVICE_URL))


async def test_the_request_timeout_is_a_client_timeout(recording_aiohttp: _RecordingClientSession) -> None:
    """aiohttp deprecated a bare number for ``timeout`` and drops it in 4.x."""
    await _session().get(SERVICE_URL, timeout=17, ignore_auth=True)

    timeout = recording_aiohttp.calls[-1]["timeout"]
    assert isinstance(timeout, ClientTimeout)
    assert timeout.total == 17


async def test_a_client_timeout_is_passed_through(recording_aiohttp: _RecordingClientSession) -> None:
    """A caller that already built a ClientTimeout keeps it."""
    await _session().get(SERVICE_URL, timeout=ClientTimeout(total=5, sock_read=2), ignore_auth=True)

    timeout = recording_aiohttp.calls[-1]["timeout"]
    assert isinstance(timeout, ClientTimeout)
    assert (timeout.total, timeout.sock_read) == (5, 2)


async def test_tls_verification_is_expressed_as_ssl(recording_aiohttp: _RecordingClientSession) -> None:
    """``verify_ssl`` is deprecated in aiohttp; the transport must send ``ssl``."""
    await _session().get(SERVICE_URL, verify_ssl=True, ignore_auth=True)

    call = recording_aiohttp.calls[-1]
    assert "verify_ssl" not in call
    assert call["ssl"] is True


async def test_disabled_tls_verification_is_expressed_as_ssl(recording_aiohttp: _RecordingClientSession) -> None:
    """A client built with ``verify_calls=False`` still disables verification."""
    await _session().get(SERVICE_URL, verify_ssl=False, ignore_auth=True)

    call = recording_aiohttp.calls[-1]
    assert "verify_ssl" not in call
    assert call["ssl"] is False


async def test_an_explicit_ssl_argument_wins(recording_aiohttp: _RecordingClientSession) -> None:
    """A caller passing ``ssl`` directly is not overridden by the translation."""
    await _session().get(SERVICE_URL, ssl=False, verify_ssl=True, ignore_auth=True)

    assert recording_aiohttp.calls[-1]["ssl"] is False


async def test_requests_without_tls_options_leave_ssl_alone(recording_aiohttp: _RecordingClientSession) -> None:
    """No TLS keyword means the connector's own context applies."""
    await _session().get(SERVICE_URL, ignore_auth=True)

    assert "ssl" not in recording_aiohttp.calls[-1]
    assert "verify_ssl" not in recording_aiohttp.calls[-1]
