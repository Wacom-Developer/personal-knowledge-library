# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Two-level token store: a process-local L1 in front of a shared L2.

When L2 is unavailable the store degrades to L1 alone, i.e. per-pod caching, instead of failing or forcing a login
per request. Only the protocols are referenced here, never a concrete backend.
"""

from typing import Optional

from knowledge import logger
from knowledge.services.cache.base import AsyncTokenStore, TokenStore, TokenStoreUnavailable


def _degraded(operation: str, exc: TokenStoreUnavailable) -> None:
    """Log a swallowed L2 failure."""
    if logger:
        logger.warning(f"Token cache L2 {operation} unavailable, continuing with L1 only: {exc}")


class TieredTokenStore:
    """Composite of a process-local ``l1`` and a shared ``l2`` store.

    Every L2 call is guarded: ``TokenStoreUnavailable`` is logged as a warning and the operation carries on with L1.
    After an L2 hit, L1 is backfilled with the remaining TTL reported by L2, so a cached entry never outlives its
    token; if L2 reports no TTL the backfill is skipped.

    Parameters
    ----------
    l1: TokenStore
        Fast, process-local tier.
    l2: TokenStore
        Shared tier, allowed to fail.
    """

    def __init__(self, l1: TokenStore, l2: TokenStore) -> None:
        self._l1 = l1
        self._l2 = l2

    @property
    def shared(self) -> bool:
        """``True`` if either tier is shared."""
        return self._l1.shared or self._l2.shared

    def get(self, key: str) -> Optional[bytes]:
        """Return the value from L1, else from L2 (backfilling L1), else ``None``."""
        value = self._l1.get(key)
        if value is not None:
            return value
        try:
            value = self._l2.get(key)
            if value is None:
                return None
            remaining = self._l2.ttl(key)
        except TokenStoreUnavailable as exc:
            _degraded("get", exc)
            return value  # a hit whose ttl lookup failed is still a valid value, just not cached in L1
        if remaining is not None and remaining > 0:
            self._l1.set(key, value, remaining)
        return value

    def set(self, key: str, value: bytes, ttl: float) -> None:
        """Store in both tiers; an L2 failure leaves the L1 write in place."""
        self._l1.set(key, value, ttl)
        try:
            self._l2.set(key, value, ttl)
        except TokenStoreUnavailable as exc:
            _degraded("set", exc)

    def delete(self, key: str) -> None:
        """Remove from both tiers; an L2 failure still clears L1."""
        self._l1.delete(key)
        try:
            self._l2.delete(key)
        except TokenStoreUnavailable as exc:
            _degraded("delete", exc)

    def ttl(self, key: str) -> Optional[float]:
        """Remaining TTL from L1 if present, else from L2, else ``None``."""
        remaining = self._l1.ttl(key)
        if remaining is not None:
            return remaining
        try:
            return self._l2.ttl(key)
        except TokenStoreUnavailable as exc:
            _degraded("ttl", exc)
            return None


class AsyncTieredTokenStore:
    """Awaitable counterpart of :class:`TieredTokenStore`.

    Parameters
    ----------
    l1: AsyncTokenStore
        Fast, process-local tier.
    l2: AsyncTokenStore
        Shared tier, allowed to fail.
    """

    def __init__(self, l1: AsyncTokenStore, l2: AsyncTokenStore) -> None:
        self._l1 = l1
        self._l2 = l2

    @property
    def shared(self) -> bool:
        """``True`` if either tier is shared."""
        return self._l1.shared or self._l2.shared

    async def get(self, key: str) -> Optional[bytes]:
        """Return the value from L1, else from L2 (backfilling L1), else ``None``."""
        value = await self._l1.get(key)
        if value is not None:
            return value
        try:
            value = await self._l2.get(key)
            if value is None:
                return None
            remaining = await self._l2.ttl(key)
        except TokenStoreUnavailable as exc:
            _degraded("get", exc)
            return value
        if remaining is not None and remaining > 0:
            await self._l1.set(key, value, remaining)
        return value

    async def set(self, key: str, value: bytes, ttl: float) -> None:
        """Store in both tiers; an L2 failure leaves the L1 write in place."""
        await self._l1.set(key, value, ttl)
        try:
            await self._l2.set(key, value, ttl)
        except TokenStoreUnavailable as exc:
            _degraded("set", exc)

    async def delete(self, key: str) -> None:
        """Remove from both tiers; an L2 failure still clears L1."""
        await self._l1.delete(key)
        try:
            await self._l2.delete(key)
        except TokenStoreUnavailable as exc:
            _degraded("delete", exc)

    async def ttl(self, key: str) -> Optional[float]:
        """Remaining TTL from L1 if present, else from L2, else ``None``."""
        remaining = await self._l1.ttl(key)
        if remaining is not None:
            return remaining
        try:
            return await self._l2.ttl(key)
        except TokenStoreUnavailable as exc:
            _degraded("ttl", exc)
            return None
