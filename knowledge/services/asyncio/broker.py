# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Process-wide PKS access-token broker for asyncio callers.

Awaitable counterpart of :class:`knowledge.services.broker.TokenBroker`, and the form an ASGI middleware actually
uses. A backend serving tens of thousands of PKS end users cannot afford a ``/user/login`` per inbound request, and
the session machinery does not fit that shape: a client binds to one session at a time, so a shared client is racy
and a client per user per request is wasteful. The broker sidesteps both by handing out a bare token string, which
the caller passes to any service method through the existing per-method ``auth_key=`` override. One service client
can then be shared by the whole process.

Steady state is one round trip per user per token lifetime: a cached token is returned without any call, and a
token approaching expiry is rotated through ``/user/refresh`` rather than re-logged in, which keeps one refresh
document per user on the service instead of one per renewal.

Nothing here blocks the event loop: the contended-lock wait is :func:`asyncio.sleep`, pacing goes through
:class:`AsyncTokenBucketLimiter`, and the only mutex held across an await is the realm lock during bootstrap, where
serialising concurrent first callers is the whole point. Per the async client's own policy there is no
transport-level retry; a caller that cannot be served from the cache makes exactly one login attempt.
"""

import asyncio
import hashlib
import inspect
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple

import orjson

from knowledge import logger
from knowledge.services.asyncio.base import AsyncServiceAPIClient
from knowledge.services.base import WacomServiceException
from knowledge.services.cache.base import (
    AsyncTokenLock,
    AsyncTokenStore,
    BrokerStats,
    CachedToken,
    TokenCipher,
    TokenStoreUnavailable,
)
from knowledge.services.cache.crypto import NullCipher
from knowledge.services.cache.limiter import AsyncTokenBucketLimiter
from knowledge.services.cache.memory import AsyncInMemoryTokenStore, AsyncInProcessLock
from knowledge.services.session import TimedSession, _decode_and_validate_token

KEY_PREFIX: str = "pks"
"""Namespace every broker key carries, so a shared Redis can hold other things."""

REFRESH_TTL_SECONDS: float = 23 * 60 * 60.0
"""Cache lifetime of a refresh token.

The service's refresh window is sliding - every rotation restamps it - and currently a day wide, so an entry that is
rewritten on each rotation and expires just inside that day keeps the chain alive indefinitely without ever handing
out a token the service has already dropped.
"""

TOKEN_FIELD: str = "token"
EXPIRES_FIELD: str = "exp"


@dataclass(frozen=True)
class _Keys:
    """The three store keys belonging to one user."""

    access: str
    refresh: str
    lock: str


class _LockOutcome(Enum):
    """What came of asking for the renewal lock.

    ``CONTENDED`` and ``UNAVAILABLE`` both mean "not holding it", but they call for opposite responses: there is a
    holder worth waiting for in the first case and provably none in the second.
    """

    HELD = auto()
    CONTENDED = auto()
    UNAVAILABLE = auto()


class AsyncTokenBroker:  # pylint: disable=too-many-instance-attributes
    """Caches PKS access tokens for many users behind one async service client.

    Parameters
    ----------
    service_url: str
        URL of the PKS instance, used only to build the default client. Cache keys are derived from the JWT claims
        instead, so a trailing slash or a separate auth host cannot split the cache.
    tenant_api_key: str
        Tenant API key used for every login.
    store: Optional[AsyncTokenStore]
        Where tokens are cached. Defaults to a process-local :class:`AsyncInMemoryTokenStore`. A shared store
        requires a real ``cipher``. Values are handled as raw bytes, so a Redis-backed store must be built on a
        binary client (``decode_responses=False``).
    cipher: Optional[TokenCipher]
        Encrypts cached values, bound to their key as associated data. Defaults to :class:`NullCipher`, which is
        only acceptable for a process-local store. Encryption is CPU-only and stays synchronous.
    lock: Optional[AsyncTokenLock]
        Best-effort mutual exclusion around a renewal, so pods do not all refresh the same user at once. Defaults
        to :class:`AsyncInProcessLock`. Losing it costs one extra login, never a wrong token.
    client: Optional[AsyncServiceAPIClient]
        Service client used for login and refresh. Defaults to a client for ``service_url``.
    rate_limit: Optional[float]
        Logins and refreshes per second allowed for calls made with ``paced=True``. ``None`` disables pacing.
    early_refresh_seconds: float
        Renew a token this long before it expires.
    early_refresh_jitter_seconds: float
        Width of the band each user's renewal is spread over. Every user gets a fixed offset inside it, derived
        from its cache key, so that a cohort of tokens minted together - a fleet restarted after a deploy, say -
        is renewed across the band instead of all at once. See :meth:`_jitter_for`.
    lock_ttl_seconds: float
        How long a renewal may hold the lock before another caller may take it.
    lock_wait_seconds: float
        How long a caller that lost the lock waits for the holder's result before logging in itself. A caller that
        could not reach the lock backend at all does not wait: there is no holder to wait for.

    Raises
    ------
    ValueError
        If ``store`` is shared but no real cipher was supplied.

    Notes
    -----
    While the lock backend is unreachable, concurrent callers for one user each renew unsynchronised, so an outage
    can produce parallel refresh chains with ``rate_limit`` as the only protection. That is a deliberate
    limitation: the lock exists to spare the service duplicated work, not to make the result correct, and stalling
    every caller for ``lock_wait_seconds`` on a holder that cannot exist would be strictly worse.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        service_url: str,
        tenant_api_key: str,
        *,
        store: Optional[AsyncTokenStore] = None,
        cipher: Optional[TokenCipher] = None,
        lock: Optional[AsyncTokenLock] = None,
        client: Optional[AsyncServiceAPIClient] = None,
        rate_limit: Optional[float] = None,
        early_refresh_seconds: float = 300.0,
        early_refresh_jitter_seconds: float = 120.0,
        lock_ttl_seconds: float = 5.0,
        lock_wait_seconds: float = 0.5,
    ) -> None:
        self._store: AsyncTokenStore = store if store is not None else AsyncInMemoryTokenStore()
        self._cipher: TokenCipher = cipher if cipher is not None else NullCipher()
        if self._store.shared and isinstance(self._cipher, NullCipher):
            raise ValueError(
                "A shared token store requires a cipher: tokens would otherwise be readable by anything with access "
                "to the backend. Pass an AesGcmCipher."
            )
        self._lock: AsyncTokenLock = lock if lock is not None else AsyncInProcessLock()
        self._client: AsyncServiceAPIClient = client if client is not None else AsyncServiceAPIClient(service_url)
        self._tenant_api_key: str = tenant_api_key
        self._limiter: Optional[AsyncTokenBucketLimiter] = (
            None if rate_limit is None else AsyncTokenBucketLimiter(rate_limit)
        )
        self._early_refresh_seconds: float = early_refresh_seconds
        self._early_refresh_jitter_seconds: float = early_refresh_jitter_seconds
        self._lock_ttl_seconds: float = lock_ttl_seconds
        self._lock_wait_seconds: float = lock_wait_seconds
        self._realm: Optional[Tuple[str, str]] = None
        self._realm_lock: asyncio.Lock = asyncio.Lock()
        self._counters: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "logins": 0,
            "refreshes": 0,
            "refresh_failures": 0,
            "lock_contentions": 0,
        }

    async def token_for(self, external_user_id: str, *, paced: bool = False) -> str:
        """Return a usable PKS access token for a user, from the cache where possible.

        Parameters
        ----------
        external_user_id: str
            External user id of the shadow user the token is for.
        paced: bool
            Take a limiter token before any login or refresh. Use it for sweeps and other bulk work, where every
            user is a cold miss, so that they queue behind the interactive traffic instead of in front of it.

        Returns
        -------
        token: str
            Access token, to be passed to service methods as ``auth_key``.

        Raises
        ------
        WacomServiceException
            If the service rejected the login.
        """
        realm = self._realm
        if realm is None:
            realm, bootstrapped = await self._bootstrap(external_user_id, paced)
            if bootstrapped is not None:
                return bootstrapped
        keys = self._keys(realm, external_user_id)
        cached = await self._read_access(keys.access)
        if cached is not None and self._is_fresh(keys.access, cached):
            self._count("hits")
            return cached.access_token
        self._count("misses")
        return await self._renew(external_user_id, keys, paced)

    async def invalidate(self, external_user_id: str, *, drop_refresh: bool = False) -> None:
        """Drop a user's cached access token, so the next call renews it.

        The refresh token is kept by default: the usual reason to invalidate is a rejected access token, and
        rotating the refresh chain is cheaper than a fresh login. Pass ``drop_refresh`` when the whole chain is
        suspect, for instance after the service rejected the refresh token itself.

        A cached entry is in any case rejected once its own expiry has passed, so this is an optimisation and never
        the only thing standing between a caller and a stale token. That matters for a tiered store, whose
        ``delete`` can clear L1 while failing on L2.

        Parameters
        ----------
        external_user_id: str
            External user id of the shadow user.
        drop_refresh: bool
            Also drop the refresh token.
        """
        realm = self._realm
        if realm is None:
            return  # nothing has been cached yet, so there is nothing to drop
        keys = self._keys(realm, external_user_id)
        await self._delete(keys.access)
        if drop_refresh:
            await self._delete(keys.refresh)

    def stats(self) -> BrokerStats:
        """Return a snapshot of the counters.

        Synchronous, because reading six integers on a single-threaded event loop needs no suspension point.

        Every :meth:`token_for` call moves exactly one of ``hits`` and ``misses``, so their sum is the number of
        calls served and ``hits / (hits + misses)`` is the cache hit ratio.
        """
        return BrokerStats(**self._counters)

    async def aclose(self) -> None:
        """Release the store, the lock and the client, where each exposes a close.

        None of the protocols declares one, so this is deliberately duck-typed rather than required. ``aclose`` is
        preferred over ``close`` and the result is awaited when it is awaitable, so a component with an ordinary
        synchronous ``close`` - the in-memory adapters, say - is released just as well as an awaitable one.
        """
        for component in (self._store, self._lock, self._client):
            closer = getattr(component, "aclose", None) or getattr(component, "close", None)
            if not callable(closer):
                continue
            try:
                result = closer()
                if inspect.isawaitable(result):
                    await result
            except TokenStoreUnavailable as exc:
                if logger:
                    logger.warning(f"Closing {type(component).__name__} failed: {exc}")

    async def __aenter__(self) -> "AsyncTokenBroker":
        """Enter the asynchronous context manager."""
        return self

    async def __aexit__(self, *exc: Any) -> None:
        """Close the broker on leaving the asynchronous context manager."""
        await self.aclose()

    # ------------------------------------------------ bootstrap ------------------------------------------------

    async def _bootstrap(self, external_user_id: str, paced: bool) -> Tuple[Tuple[str, str], Optional[str]]:
        """Learn the realm - issuer and tenant id - from a freshly minted JWT.

        Cache keys are derived from claims, and the tenant *id* is not the tenant *API key* the constructor was
        given, so a cold process cannot compute a key for a user it has never seen. The one login this costs is the
        caller's own login, not an extra one: its tokens are cached and returned.

        The whole thing runs under a lock, so concurrent first callers produce one login rather than one each; the
        losers find the realm resolved and take the ordinary read path, which hits the cache. This is the one place
        a mutex is deliberately held across a network round trip, because serialising those callers is the point.

        Returns
        -------
        realm: Tuple[str, str]
            Issuer and tenant id.
        token: Optional[str]
            The access token, but only for the caller that performed the login.
        """
        async with self._realm_lock:
            if self._realm is not None:
                return self._realm, None
            self._count("misses")
            access, refresh, claims = await self._login(external_user_id, paced)
            realm = (str(claims["iss"]), str(claims["tenant"]))
            token = await self._write(self._keys(realm, external_user_id), access, refresh, claims)
            self._realm = realm
            return realm, token

    @staticmethod
    def _keys(realm: Tuple[str, str], external_user_id: str) -> _Keys:
        """Derive the store keys for a user.

        The session id is the one :class:`TimedSession` computes, which keeps the broker and the session machinery
        in step and keeps external user ids out of a shared backend.
        """
        issuer, tenant_id = realm
        session_id = TimedSession._session_id_(issuer, tenant_id, external_user_id)
        return _Keys(
            access=f"{KEY_PREFIX}:{session_id}:a",
            refresh=f"{KEY_PREFIX}:{session_id}:r",
            lock=f"{KEY_PREFIX}:{session_id}:lk",
        )

    # ------------------------------------------------ read path ------------------------------------------------

    def _jitter_for(self, key: str) -> float:
        """Return this entry's renewal offset: a stable value in ``[0, early_refresh_jitter_seconds)``.

        Derived from a SHA-256 of the cache key - not :func:`hash`, whose seed differs per process - so every pod
        computes the same offset for a given user and a different one for the next user. That is what spreads a
        cohort of tokens minted together; drawing a fresh random offset per read would not, because a user read
        many times a second renews on the first draw that clears the remaining life, which is the earliest edge of
        the band and the same instant for every pod.
        """
        if self._early_refresh_jitter_seconds <= 0:
            return 0.0
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        fraction = int.from_bytes(digest[:8], "big") / 2**64
        return fraction * self._early_refresh_jitter_seconds

    def _is_fresh(self, key: str, cached: CachedToken) -> bool:
        """Whether a cached token has enough life left to be handed out."""
        margin = self._early_refresh_seconds + self._jitter_for(key)
        return cached.expires_at - time.time() > margin

    async def _read_access(self, key: str) -> Optional[CachedToken]:
        """Return the cached access token, or ``None`` if it is absent, unreadable or malformed."""
        raw = await self._get(key)
        if raw is None:
            return None
        try:
            payload = orjson.loads(self._cipher.decrypt(raw, key.encode("utf-8")))
            token = payload[TOKEN_FIELD]
            if not isinstance(token, str):
                raise ValueError("Cached access token is not a string.")
            return CachedToken(access_token=token, expires_at=float(payload[EXPIRES_FIELD]))
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # The cipher's failure modes are its own - a wrong key, a value moved to another user's key, plain
            # corruption - and none of them should fail a request that a login can serve.
            if logger:
                logger.warning(f"Unreadable cached access token, treating as a miss: {exc}")
            return None

    async def _read_refresh(self, key: str) -> Optional[str]:
        """Return the cached refresh token, or ``None`` if it is absent or unreadable."""
        raw = await self._get(key)
        if raw is None:
            return None
        try:
            return self._cipher.decrypt(raw, key.encode("utf-8")).decode("utf-8")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if logger:
                logger.warning(f"Unreadable cached refresh token, treating as a miss: {exc}")
            return None

    async def _renew(self, external_user_id: str, keys: _Keys, paced: bool) -> str:
        """Renew a user's token, under the lock where it can be had.

        The lock exists to spare the service a pile of parallel refresh chains, not to make the result correct: a
        caller that loses it waits briefly for the holder's write and otherwise just logs in. It never retries.
        """
        outcome = await self._acquire(keys.lock)
        if outcome is _LockOutcome.HELD:
            acquired_at = time.monotonic()
            try:
                return await self._renew_as_holder(external_user_id, keys, paced)
            finally:
                await self._release(keys.lock, acquired_at)
        if outcome is _LockOutcome.UNAVAILABLE:
            # Nobody can be holding a lock whose backend is unreachable, so there is no holder whose write is worth
            # waiting for. Renewing straight away keeps the latency of a degraded backend off the caller, and the
            # outage is already counted where it belongs rather than as contention.
            return await self._renew_as_holder(external_user_id, keys, paced)
        self._count("lock_contentions")
        await asyncio.sleep(self._lock_wait_seconds)  # a suspension, not a stall: other tasks keep running
        cached = await self._read_access(keys.access)
        if cached is not None and self._is_fresh(keys.access, cached):
            # Deliberately not counted as a hit: the call already counted a miss, and every call should move
            # exactly one of the two counters, or the hit ratio stops meaning anything.
            return cached.access_token
        access, refresh, claims = await self._login(external_user_id, paced)
        return await self._write(keys, access, refresh, claims)

    async def _renew_as_holder(self, external_user_id: str, keys: _Keys, paced: bool) -> str:
        """Rotate the refresh chain, falling back to a login when there is none or the service rejects it."""
        rotated: Optional[Tuple[str, str]] = None
        cached_refresh = await self._read_refresh(keys.refresh)
        if cached_refresh is not None:
            try:
                await self._pace(paced)
                access, refresh, _ = await self._client.refresh_token(cached_refresh)
                rotated = (access, refresh)
            except WacomServiceException as exc:
                self._count("refresh_failures")
                if logger:
                    logger.info(f"Refresh rejected, falling back to a login: {exc}")
                await self._delete(keys.refresh)
        if rotated is not None:
            self._count("refreshes")
            return await self._write(keys, rotated[0], rotated[1], self._claims(rotated[0]))
        access, refresh, claims = await self._login(external_user_id, paced)
        return await self._write(keys, access, refresh, claims)

    async def _login(self, external_user_id: str, paced: bool) -> Tuple[str, str, Dict[str, Any]]:
        """Log the user in and return the tokens together with the access token's claims."""
        await self._pace(paced)
        access, refresh, _ = await self._client.request_user_token(self._tenant_api_key, external_user_id)
        self._count("logins")
        return access, refresh, self._claims(access)

    async def _pace(self, paced: bool) -> None:
        """Take a limiter token when the call is paced and a limiter is configured."""
        if paced and self._limiter is not None:
            await self._limiter.acquire()

    @staticmethod
    def _claims(access_token: str) -> Dict[str, Any]:
        """Decode a PKS access token and check that it carries the claims the cache keys are built from."""
        return _decode_and_validate_token(access_token)

    async def _write(self, keys: _Keys, access_token: str, refresh_token: str, claims: Dict[str, Any]) -> str:
        """Cache both tokens and return the access token.

        The access entry lives exactly as long as the token does, taken from the ``exp`` claim rather than from any
        assumed lifetime: the service's token validity is deployment configuration and can change under us.
        """
        expires_at = float(claims["exp"])
        ttl = expires_at - time.time()
        if ttl > 0:
            payload = orjson.dumps({TOKEN_FIELD: access_token, EXPIRES_FIELD: expires_at})
            await self._set(keys.access, self._cipher.encrypt(payload, keys.access.encode("utf-8")), ttl)
        elif logger:
            logger.warning("Received an already-expired access token; not caching it.")
        await self._set(
            keys.refresh,
            self._cipher.encrypt(refresh_token.encode("utf-8"), keys.refresh.encode("utf-8")),
            REFRESH_TTL_SECONDS,
        )
        return access_token

    # --------------------------------------- backend calls, all optional ---------------------------------------

    async def _get(self, key: str) -> Optional[bytes]:
        """Read from the store, treating an unavailable backend as a miss."""
        try:
            return await self._store.get(key)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Token store unavailable on read, treating as a miss: {exc}")
            return None

    async def _set(self, key: str, value: bytes, ttl: float) -> None:
        """Write to the store; a failure costs a later cache miss, never this request."""
        try:
            await self._store.set(key, value, ttl)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Token store unavailable on write, token not cached: {exc}")

    async def _delete(self, key: str) -> None:
        """Drop a key from the store, tolerating an unavailable backend."""
        try:
            await self._store.delete(key)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Token store unavailable on delete, entry left in place: {exc}")

    async def _acquire(self, key: str) -> _LockOutcome:
        """Try to take the renewal lock, distinguishing a held lock from an unreachable backend."""
        try:
            acquired = await self._lock.acquire(key, self._lock_ttl_seconds)
            return _LockOutcome.HELD if acquired else _LockOutcome.CONTENDED
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Lock backend unavailable, renewing without the lock: {exc}")
            return _LockOutcome.UNAVAILABLE

    async def _release(self, key: str, acquired_at: float) -> None:
        """Release the renewal lock. Best effort: a failed release must never fail the caller's request.

        A renewal that outran ``lock_ttl_seconds`` no longer holds the lock it took, and the lock protocol's
        ``release`` is not owner-aware, so releasing now could free a lock somebody else has since acquired. Such a
        lock is already expiring on its own, so the safe move is to leave it alone.
        """
        if time.monotonic() - acquired_at > self._lock_ttl_seconds:
            if logger:
                logger.warning("Renewal outlived the lock TTL; leaving the lock to expire rather than freeing it.")
            return
        try:
            await self._lock.release(key)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Lock backend unavailable on release, lock left to expire: {exc}")

    def _count(self, counter: str) -> None:
        """Increment a counter.

        No mutex: the event loop runs one task at a time and there is no await between the read and the write, so
        the increment is atomic with respect to every other task.
        """
        self._counters[counter] += 1
