# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Redis-backed token store and lock, available through the optional ``cache`` extra.

All four classes take an already-configured ``redis.Redis`` (sync) or ``redis.asyncio.Redis`` (async) client, so the
caller owns connection, pool, TLS and timeout settings. Every backend failure surfaces as
:class:`~knowledge.services.cache.base.TokenStoreUnavailable`, which lets a tiered store degrade to per-pod caching
when Redis is down.

This module is never imported by ``knowledge.services.cache`` itself.
"""

import secrets
import threading
from typing import Any, Dict, Optional, Tuple, Type

from knowledge import logger
from knowledge.services.cache.base import TokenStoreUnavailable

# Compare-and-delete. Despite the name, ``EVAL`` here is the Redis command running this Lua script server-side; it is
# not Python's ``eval``. The key is only deleted while it still holds the caller's token, so a holder whose TTL has
# lapsed and whose lock was re-acquired elsewhere cannot free the new holder's lock.
_RELEASE_SCRIPT: str = (
    "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
)
_LOCK_TOKEN_BYTES: int = 16


def _backend_errors() -> Tuple[Type[BaseException], ...]:
    """Import ``redis`` lazily and return the exception types that mean the backend is unavailable."""
    try:
        from redis.exceptions import RedisError  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError(
            "The Redis token cache requires the 'redis' package. Install it with the 'cache' extra: "
            "pip install personal-knowledge-library[cache]"
        ) from exc
    return RedisError, OSError


def _unavailable(operation: str, exc: BaseException) -> TokenStoreUnavailable:
    """Build the exception raised for a failed backend call, and log it."""
    if logger:
        logger.warning(f"Redis token cache {operation} failed: {exc}")
    return TokenStoreUnavailable(f"Redis {operation} failed: {exc}")


def _expiry_ms(ttl: float) -> int:
    """Convert seconds to a positive millisecond count; Redis rejects an expiry of zero."""
    return max(1, int(ttl * 1000))


def _remaining_seconds(pttl: int) -> Optional[float]:
    """Map a ``PTTL`` reply to seconds; ``-2`` (no key) and ``-1`` (no expiry) become ``None``."""
    if pttl < 0:
        return None
    return pttl / 1000.0


class RedisTokenStore:
    """Token store backed by Redis, shared across processes.

    Parameters
    ----------
    client: redis.Redis
        A configured synchronous Redis client.
    """

    shared: bool = True

    def __init__(self, client: Any) -> None:
        self._errors = _backend_errors()
        self._client = client

    def get(self, key: str) -> Optional[bytes]:
        """Return the value, or ``None`` if absent or expired."""
        try:
            value = self._client.get(key)
        except self._errors as exc:
            raise _unavailable("get", exc) from exc
        return None if value is None else bytes(value)

    def set(self, key: str, value: bytes, ttl: float) -> None:
        """Store ``value`` for ``ttl`` seconds."""
        try:
            self._client.set(key, value, px=_expiry_ms(ttl))
        except self._errors as exc:
            raise _unavailable("set", exc) from exc

    def delete(self, key: str) -> None:
        """Remove ``key`` if present."""
        try:
            self._client.delete(key)
        except self._errors as exc:
            raise _unavailable("delete", exc) from exc

    def ttl(self, key: str) -> Optional[float]:
        """Remaining time-to-live in seconds; ``None`` if the key is absent or carries no expiry."""
        try:
            pttl = self._client.pttl(key)
        except self._errors as exc:
            raise _unavailable("pttl", exc) from exc
        return _remaining_seconds(pttl)


class AsyncRedisTokenStore:
    """Awaitable counterpart of :class:`RedisTokenStore`.

    Parameters
    ----------
    client: redis.asyncio.Redis
        A configured asynchronous Redis client.
    """

    shared: bool = True

    def __init__(self, client: Any) -> None:
        self._errors = _backend_errors()
        self._client = client

    async def get(self, key: str) -> Optional[bytes]:
        """Return the value, or ``None`` if absent or expired."""
        try:
            value = await self._client.get(key)
        except self._errors as exc:
            raise _unavailable("get", exc) from exc
        return None if value is None else bytes(value)

    async def set(self, key: str, value: bytes, ttl: float) -> None:
        """Store ``value`` for ``ttl`` seconds."""
        try:
            await self._client.set(key, value, px=_expiry_ms(ttl))
        except self._errors as exc:
            raise _unavailable("set", exc) from exc

    async def delete(self, key: str) -> None:
        """Remove ``key`` if present."""
        try:
            await self._client.delete(key)
        except self._errors as exc:
            raise _unavailable("delete", exc) from exc

    async def ttl(self, key: str) -> Optional[float]:
        """Remaining time-to-live in seconds; ``None`` if the key is absent or carries no expiry."""
        try:
            pttl = await self._client.pttl(key)
        except self._errors as exc:
            raise _unavailable("pttl", exc) from exc
        return _remaining_seconds(pttl)


class RedisLock:
    """Best-effort cross-process lock using ``SET NX PX`` and a compare-and-delete release.

    The token written on acquire is remembered per key, and release only deletes the key while it still holds that
    token. A lock lost to TTL expiry therefore costs at most a duplicate login; it never frees another holder's lock.

    Parameters
    ----------
    client: redis.Redis
        A configured synchronous Redis client.
    """

    def __init__(self, client: Any) -> None:
        self._errors = _backend_errors()
        self._client = client
        self._guard = threading.Lock()
        self._tokens: Dict[str, str] = {}

    def acquire(self, key: str, ttl: float) -> bool:
        """Try to take the lock for at most ``ttl`` seconds; ``False`` if somebody else holds it."""
        token = secrets.token_hex(_LOCK_TOKEN_BYTES)
        try:
            acquired = self._client.set(key, token, nx=True, px=_expiry_ms(ttl))
        except self._errors as exc:
            raise _unavailable("lock acquire", exc) from exc
        if not acquired:
            return False
        with self._guard:
            self._tokens[key] = token
        return True

    def release(self, key: str) -> None:
        """Release the lock if this instance still holds it."""
        with self._guard:
            token = self._tokens.pop(key, None)
        if token is None:
            return
        try:
            self._client.eval(_RELEASE_SCRIPT, 1, key, token)
        except self._errors as exc:
            raise _unavailable("lock release", exc) from exc


class AsyncRedisLock:
    """Awaitable counterpart of :class:`RedisLock`.

    Parameters
    ----------
    client: redis.asyncio.Redis
        A configured asynchronous Redis client.
    """

    def __init__(self, client: Any) -> None:
        self._errors = _backend_errors()
        self._client = client
        self._tokens: Dict[str, str] = {}

    async def acquire(self, key: str, ttl: float) -> bool:
        """Try to take the lock for at most ``ttl`` seconds; ``False`` if somebody else holds it."""
        token = secrets.token_hex(_LOCK_TOKEN_BYTES)
        try:
            acquired = await self._client.set(key, token, nx=True, px=_expiry_ms(ttl))
        except self._errors as exc:
            raise _unavailable("lock acquire", exc) from exc
        if not acquired:
            return False
        self._tokens[key] = token
        return True

    async def release(self, key: str) -> None:
        """Release the lock if this instance still holds it."""
        token = self._tokens.pop(key, None)
        if token is None:
            return
        try:
            await self._client.eval(_RELEASE_SCRIPT, 1, key, token)
        except self._errors as exc:
            raise _unavailable("lock release", exc) from exc
