# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Process-wide PKS access-token broker.

A backend serving tens of thousands of PKS end users cannot afford a ``/user/login`` per inbound request, and the
session machinery does not fit that shape: a client binds to one session at a time, so a shared client is racy and a
client per user per request is wasteful. The broker sidesteps both by handing out a bare token string, which the
caller passes to any service method through the existing per-method ``auth_key=`` override. One service client can
then be shared by the whole process.

Steady state is one round trip per user per token lifetime: a cached token is returned without any call, and a token
approaching expiry is rotated through ``/user/refresh`` rather than re-logged in, which keeps one refresh document
per user on the service instead of one per renewal.
"""

import random
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import orjson

from knowledge import logger
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException
from knowledge.services.cache.base import (
    BrokerStats,
    CachedToken,
    TokenCipher,
    TokenLock,
    TokenStore,
    TokenStoreUnavailable,
)
from knowledge.services.cache.crypto import NullCipher
from knowledge.services.cache.limiter import TokenBucketLimiter
from knowledge.services.cache.memory import InMemoryTokenStore, InProcessLock
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


class TokenBroker:  # pylint: disable=too-many-instance-attributes
    """Caches PKS access tokens for many users behind one service client.

    Parameters
    ----------
    service_url: str
        URL of the PKS instance, used only to build the default client. Cache keys are derived from the JWT claims
        instead, so a trailing slash or a separate auth host cannot split the cache.
    tenant_api_key: str
        Tenant API key used for every login.
    store: Optional[TokenStore]
        Where tokens are cached. Defaults to a process-local :class:`InMemoryTokenStore`. A shared store requires a
        real ``cipher``. Values are handled as raw bytes, so a Redis-backed store must be built on a binary client
        (``decode_responses=False``).
    cipher: Optional[TokenCipher]
        Encrypts cached values, bound to their key as associated data. Defaults to :class:`NullCipher`, which is
        only acceptable for a process-local store.
    lock: Optional[TokenLock]
        Best-effort mutual exclusion around a renewal, so pods do not all refresh the same user at once. Defaults to
        :class:`InProcessLock`. Losing it costs one extra login, never a wrong token.
    client: Optional[WacomServiceAPIClient]
        Service client used for login and refresh. Defaults to a client for ``service_url``.
    rate_limit: Optional[float]
        Logins and refreshes per second allowed for calls made with ``paced=True``. ``None`` disables pacing.
    early_refresh_seconds: float
        Renew a token this long before it expires.
    early_refresh_jitter_seconds: float
        Upper bound of a random addition to ``early_refresh_seconds``, drawn per read, so that pods holding tokens
        minted together do not renew them together.
    lock_ttl_seconds: float
        How long a renewal may hold the lock before another caller may take it.
    lock_wait_seconds: float
        How long a caller that lost the lock waits for the holder's result before logging in itself.

    Raises
    ------
    ValueError
        If ``store`` is shared but no real cipher was supplied.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        service_url: str,
        tenant_api_key: str,
        *,
        store: Optional[TokenStore] = None,
        cipher: Optional[TokenCipher] = None,
        lock: Optional[TokenLock] = None,
        client: Optional[WacomServiceAPIClient] = None,
        rate_limit: Optional[float] = None,
        early_refresh_seconds: float = 300.0,
        early_refresh_jitter_seconds: float = 120.0,
        lock_ttl_seconds: float = 5.0,
        lock_wait_seconds: float = 0.5,
    ) -> None:
        self._store: TokenStore = store if store is not None else InMemoryTokenStore()
        self._cipher: TokenCipher = cipher if cipher is not None else NullCipher()
        if self._store.shared and isinstance(self._cipher, NullCipher):
            raise ValueError(
                "A shared token store requires a cipher: tokens would otherwise be readable by anything with access "
                "to the backend. Pass an AesGcmCipher."
            )
        self._lock: TokenLock = lock if lock is not None else InProcessLock()
        self._client: WacomServiceAPIClient = client if client is not None else WacomServiceAPIClient(service_url)
        self._tenant_api_key: str = tenant_api_key
        self._limiter: Optional[TokenBucketLimiter] = None if rate_limit is None else TokenBucketLimiter(rate_limit)
        self._early_refresh_seconds: float = early_refresh_seconds
        self._early_refresh_jitter_seconds: float = early_refresh_jitter_seconds
        self._lock_ttl_seconds: float = lock_ttl_seconds
        self._lock_wait_seconds: float = lock_wait_seconds
        self._realm: Optional[Tuple[str, str]] = None
        self._realm_lock: threading.Lock = threading.Lock()
        self._counters: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "logins": 0,
            "refreshes": 0,
            "refresh_failures": 0,
            "lock_contentions": 0,
        }
        self._counters_lock: threading.Lock = threading.Lock()

    def token_for(self, external_user_id: str, *, paced: bool = False) -> str:
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
            realm, bootstrapped = self._bootstrap(external_user_id, paced)
            if bootstrapped is not None:
                return bootstrapped
        keys = self._keys(realm, external_user_id)
        cached = self._read_access(keys.access)
        if cached is not None and self._is_fresh(cached):
            self._count("hits")
            return cached.access_token
        self._count("misses")
        return self._renew(external_user_id, keys, paced)

    def invalidate(self, external_user_id: str, *, drop_refresh: bool = False) -> None:
        """Drop a user's cached access token, so the next call renews it.

        The refresh token is kept by default: the usual reason to invalidate is a rejected access token, and
        rotating the refresh chain is cheaper than a fresh login. Pass ``drop_refresh`` when the whole chain is
        suspect, for instance after the service rejected the refresh token itself.

        A cached entry is in any case rejected once its own expiry has passed, so this is an optimisation and never
        the only thing standing between a caller and a stale token.

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
        self._delete(keys.access)
        if drop_refresh:
            self._delete(keys.refresh)

    def stats(self) -> BrokerStats:
        """Return a snapshot of the counters.

        Every :meth:`token_for` call moves exactly one of ``hits`` and ``misses``, so their sum is the number of
        calls served and ``hits / (hits + misses)`` is the cache hit ratio.
        """
        with self._counters_lock:
            return BrokerStats(**self._counters)

    def close(self) -> None:
        """Release the store, the lock and the client, where each exposes a ``close``.

        None of the protocols declares one, so this is deliberately duck-typed rather than required.
        """
        for component in (self._store, self._lock, self._client):
            closer = getattr(component, "close", None)
            if not callable(closer):
                continue
            try:
                closer()
            except TokenStoreUnavailable as exc:
                if logger:
                    logger.warning(f"Closing {type(component).__name__} failed: {exc}")

    def __enter__(self) -> "TokenBroker":
        """Enter the context manager."""
        return self

    def __exit__(self, *exc: Any) -> None:
        """Close the broker on leaving the context manager."""
        self.close()

    # ------------------------------------------------ bootstrap ------------------------------------------------

    def _bootstrap(self, external_user_id: str, paced: bool) -> Tuple[Tuple[str, str], Optional[str]]:
        """Learn the realm - issuer and tenant id - from a freshly minted JWT.

        Cache keys are derived from claims, and the tenant *id* is not the tenant *API key* the constructor was
        given, so a cold process cannot compute a key for a user it has never seen. The one login this costs is the
        caller's own login, not an extra one: its tokens are cached and returned.

        The whole thing runs under a lock, so concurrent first callers produce one login rather than one each; the
        losers find the realm resolved and take the ordinary read path, which hits the cache.

        Returns
        -------
        realm: Tuple[str, str]
            Issuer and tenant id.
        token: Optional[str]
            The access token, but only for the caller that performed the login.
        """
        with self._realm_lock:
            if self._realm is not None:
                return self._realm, None
            self._count("misses")
            access, refresh, claims = self._login(external_user_id, paced)
            realm = (str(claims["iss"]), str(claims["tenant"]))
            token = self._write(self._keys(realm, external_user_id), access, refresh, claims)
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

    def _is_fresh(self, cached: CachedToken) -> bool:
        """Whether a cached token has enough life left to be handed out."""
        margin = self._early_refresh_seconds + random.uniform(0.0, self._early_refresh_jitter_seconds)
        return cached.expires_at - time.time() > margin

    def _read_access(self, key: str) -> Optional[CachedToken]:
        """Return the cached access token, or ``None`` if it is absent, unreadable or malformed."""
        raw = self._get(key)
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

    def _read_refresh(self, key: str) -> Optional[str]:
        """Return the cached refresh token, or ``None`` if it is absent or unreadable."""
        raw = self._get(key)
        if raw is None:
            return None
        try:
            return self._cipher.decrypt(raw, key.encode("utf-8")).decode("utf-8")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if logger:
                logger.warning(f"Unreadable cached refresh token, treating as a miss: {exc}")
            return None

    def _renew(self, external_user_id: str, keys: _Keys, paced: bool) -> str:
        """Renew a user's token, under the lock where it can be had.

        The lock exists to spare the service a pile of parallel refresh chains, not to make the result correct: a
        caller that loses it waits briefly for the holder's write and otherwise just logs in. It never retries.
        """
        if self._acquire(keys.lock):
            acquired_at = time.monotonic()
            try:
                return self._renew_as_holder(external_user_id, keys, paced)
            finally:
                self._release(keys.lock, acquired_at)
        self._count("lock_contentions")
        time.sleep(self._lock_wait_seconds)
        cached = self._read_access(keys.access)
        if cached is not None and self._is_fresh(cached):
            # Deliberately not counted as a hit: the call already counted a miss, and every call should move
            # exactly one of the two counters, or the hit ratio stops meaning anything.
            return cached.access_token
        access, refresh, claims = self._login(external_user_id, paced)
        return self._write(keys, access, refresh, claims)

    def _renew_as_holder(self, external_user_id: str, keys: _Keys, paced: bool) -> str:
        """Rotate the refresh chain, falling back to a login when there is none or the service rejects it."""
        rotated: Optional[Tuple[str, str]] = None
        cached_refresh = self._read_refresh(keys.refresh)
        if cached_refresh is not None:
            try:
                self._pace(paced)
                access, refresh, _ = self._client.refresh_token(cached_refresh)
                rotated = (access, refresh)
            except WacomServiceException as exc:
                self._count("refresh_failures")
                if logger:
                    logger.info(f"Refresh rejected, falling back to a login: {exc}")
                self._delete(keys.refresh)
        if rotated is not None:
            self._count("refreshes")
            return self._write(keys, rotated[0], rotated[1], self._claims(rotated[0]))
        access, refresh, claims = self._login(external_user_id, paced)
        return self._write(keys, access, refresh, claims)

    def _login(self, external_user_id: str, paced: bool) -> Tuple[str, str, Dict[str, Any]]:
        """Log the user in and return the tokens together with the access token's claims."""
        self._pace(paced)
        access, refresh, _ = self._client.request_user_token(self._tenant_api_key, external_user_id)
        self._count("logins")
        return access, refresh, self._claims(access)

    def _pace(self, paced: bool) -> None:
        """Take a limiter token when the call is paced and a limiter is configured."""
        if paced and self._limiter is not None:
            self._limiter.acquire()

    @staticmethod
    def _claims(access_token: str) -> Dict[str, Any]:
        """Decode a PKS access token and check that it carries the claims the cache keys are built from."""
        return _decode_and_validate_token(access_token)

    def _write(self, keys: _Keys, access_token: str, refresh_token: str, claims: Dict[str, Any]) -> str:
        """Cache both tokens and return the access token.

        The access entry lives exactly as long as the token does, taken from the ``exp`` claim rather than from any
        assumed lifetime: the service's token validity is deployment configuration and can change under us.
        """
        expires_at = float(claims["exp"])
        ttl = expires_at - time.time()
        if ttl > 0:
            payload = orjson.dumps({TOKEN_FIELD: access_token, EXPIRES_FIELD: expires_at})
            self._set(keys.access, self._cipher.encrypt(payload, keys.access.encode("utf-8")), ttl)
        elif logger:
            logger.warning("Received an already-expired access token; not caching it.")
        self._set(
            keys.refresh,
            self._cipher.encrypt(refresh_token.encode("utf-8"), keys.refresh.encode("utf-8")),
            REFRESH_TTL_SECONDS,
        )
        return access_token

    # --------------------------------------- backend calls, all optional ---------------------------------------

    def _get(self, key: str) -> Optional[bytes]:
        """Read from the store, treating an unavailable backend as a miss."""
        try:
            return self._store.get(key)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Token store unavailable on read, treating as a miss: {exc}")
            return None

    def _set(self, key: str, value: bytes, ttl: float) -> None:
        """Write to the store; a failure costs a later cache miss, never this request."""
        try:
            self._store.set(key, value, ttl)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Token store unavailable on write, token not cached: {exc}")

    def _delete(self, key: str) -> None:
        """Drop a key from the store, tolerating an unavailable backend."""
        try:
            self._store.delete(key)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Token store unavailable on delete, entry left in place: {exc}")

    def _acquire(self, key: str) -> bool:
        """Try to take the renewal lock; an unavailable backend counts as not holding it."""
        try:
            return self._lock.acquire(key, self._lock_ttl_seconds)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Lock backend unavailable, proceeding without the lock: {exc}")
            return False

    def _release(self, key: str, acquired_at: float) -> None:
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
            self._lock.release(key)
        except TokenStoreUnavailable as exc:
            if logger:
                logger.warning(f"Lock backend unavailable on release, lock left to expire: {exc}")

    def _count(self, counter: str) -> None:
        """Increment a counter."""
        with self._counters_lock:
            self._counters[counter] += 1
