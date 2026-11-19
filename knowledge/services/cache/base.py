# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Protocols and value types shared by the token cache implementations.

The protocols are structural documentation, not ``isinstance`` targets, so they are deliberately not
``runtime_checkable``.
"""

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class CachedToken:
    """An access token and its expiry.

    The refresh token is stored separately as bare bytes under its own key, because the two have different TTLs.

    Parameters
    ----------
    access_token: str
        The PKS access token.
    expires_at: float
        Expiry in epoch seconds, taken from the JWT ``exp`` claim.
    """

    access_token: str
    expires_at: float


@dataclass(frozen=True)
class BrokerStats:
    """Counters exposed by a token broker."""

    hits: int
    misses: int
    logins: int
    refreshes: int
    refresh_failures: int
    lock_contentions: int


class TokenStoreUnavailable(Exception):
    """Raised by a store whose backend is unreachable."""


class TokenCipher(Protocol):
    """Authenticated encryption of cache values."""

    def encrypt(self, plaintext: bytes, aad: bytes) -> bytes:
        """Encrypt ``plaintext``, binding it to ``aad``."""
        ...

    def decrypt(self, ciphertext: bytes, aad: bytes) -> bytes:
        """Decrypt ``ciphertext``; raises if it was not produced for the same ``aad``."""
        ...


class TokenStore(Protocol):
    """Key/value store with per-entry expiry."""

    @property
    def shared(self) -> bool:
        """``True`` when other processes can read this store."""
        ...

    def get(self, key: str) -> Optional[bytes]:
        """Return the value, or ``None`` if absent or expired."""
        ...

    def set(self, key: str, value: bytes, ttl: float) -> None:
        """Store ``value`` for ``ttl`` seconds."""
        ...

    def delete(self, key: str) -> None:
        """Remove ``key`` if present."""
        ...

    def ttl(self, key: str) -> Optional[float]:
        """Remaining time-to-live in seconds; ``None`` if the key is absent or carries no expiry."""
        ...


class TokenLock(Protocol):
    """Non-blocking, expiring mutual exclusion keyed by string."""

    def acquire(self, key: str, ttl: float) -> bool:
        """Try to take the lock for at most ``ttl`` seconds; ``False`` if somebody else holds it."""
        ...

    def release(self, key: str) -> None:
        """Release the lock."""
        ...


class AsyncTokenStore(Protocol):
    """Awaitable counterpart of :class:`TokenStore`."""

    @property
    def shared(self) -> bool:
        """``True`` when other processes can read this store."""
        ...

    async def get(self, key: str) -> Optional[bytes]:
        """Return the value, or ``None`` if absent or expired."""
        ...

    async def set(self, key: str, value: bytes, ttl: float) -> None:
        """Store ``value`` for ``ttl`` seconds."""
        ...

    async def delete(self, key: str) -> None:
        """Remove ``key`` if present."""
        ...

    async def ttl(self, key: str) -> Optional[float]:
        """Remaining time-to-live in seconds; ``None`` if the key is absent or carries no expiry."""
        ...


class AsyncTokenLock(Protocol):
    """Awaitable counterpart of :class:`TokenLock`."""

    async def acquire(self, key: str, ttl: float) -> bool:
        """Try to take the lock for at most ``ttl`` seconds; ``False`` if somebody else holds it."""
        ...

    async def release(self, key: str) -> None:
        """Release the lock."""
        ...
