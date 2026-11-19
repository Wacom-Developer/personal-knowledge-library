# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the synchronous token broker; no Redis, no network, no live PKS."""

import itertools
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import jwt
import orjson
import pytest

from knowledge.services import broker as broker_module
from knowledge.services.base import WacomServiceException
from knowledge.services.broker import TokenBroker
from knowledge.services.cache.base import BrokerStats, TokenStoreUnavailable
from knowledge.services.cache.crypto import AesGcmCipher, NullCipher
from knowledge.services.cache.limiter import TokenBucketLimiter
from knowledge.services.cache.memory import InMemoryTokenStore, InProcessLock
from knowledge.services.session import TimedSession

ISSUER: str = "https://issuer.example.com/graph"
TENANT_ID: str = "4711-tenant"
TENANT_API_KEY: str = "tenant-api-key"
SERVICE_URL: str = "https://configured.example.com"
USER: str = "user@example.com"
OTHER_USER: str = "other@example.com"


_SERIAL = itertools.count(1)


def mint(external_user_id: str, ttl: float = 3600.0, issuer: str = ISSUER, tenant: str = TENANT_ID) -> str:
    """Mint an unsigned JWT carrying the five claims the session machinery requires.

    A serial ``jti`` makes every minted token distinct, as a real one would be; two tokens issued within the same
    second would otherwise be byte-identical and no test could tell a reissue from a cache hit.
    """
    return jwt.encode(
        {
            "tenant": tenant,
            "roles": "User",
            "exp": int(time.time() + ttl),
            "iss": issuer,
            "ext-sub": external_user_id,
            "jti": next(_SERIAL),
        },
        key="",
        algorithm="none",
    )


def forge(access_token: str, expires_at: float) -> bytes:
    """Build a cache entry by hand, as the broker writes it when no cipher is configured.

    Only used to plant an entry the broker itself would refuse to write; every test that forges one also asserts
    the same shape is accepted, so a change to the payload format cannot leave such a test silently passing.
    """
    return orjson.dumps({"token": access_token, "exp": expires_at})


def claims_of(access_token: str) -> Dict[str, object]:
    """Decode a token minted by :func:`mint`."""
    decoded: Dict[str, object] = jwt.decode(access_token, options={"verify_signature": False})
    return decoded


class FakeClient:
    """Stand-in for ``WacomServiceAPIClient`` counting logins and refreshes.

    Counters are lock-guarded so a broker that logs in concurrently cannot hide the extra calls behind a lost
    increment.
    """

    def __init__(
        self, lifetime: float = 3600.0, issuer: str = ISSUER, tenant: str = TENANT_ID, login_delay: float = 0.0
    ) -> None:
        self.lifetime: float = lifetime
        self.issuer: str = issuer
        self.tenant: str = tenant
        self.login_delay: float = login_delay
        self.logins: int = 0
        self.refreshes: int = 0
        self.login_error: Optional[Exception] = None
        self.refresh_error: Optional[Exception] = None
        self.closed: bool = False
        self.subjects: Dict[str, str] = {}
        self._serial = itertools.count(1)
        self._guard = threading.Lock()

    def _issue(self, external_id: str) -> Tuple[str, str, datetime]:
        access = mint(external_id, ttl=self.lifetime, issuer=self.issuer, tenant=self.tenant)
        refresh = f"refresh-{external_id}-{next(self._serial)}"
        self.subjects[refresh] = external_id
        return access, refresh, datetime.now(timezone.utc) + timedelta(seconds=self.lifetime)

    def request_user_token(self, tenant_api_key: str, external_id: str, timeout: int = 60) -> Tuple[str, str, datetime]:
        """Login, taking ``login_delay`` seconds as a real network round trip would."""
        assert tenant_api_key == TENANT_API_KEY
        assert timeout > 0
        time.sleep(self.login_delay)  # outside the guard, so concurrent callers really do overlap
        with self._guard:
            self.logins += 1
            if self.login_error is not None:
                raise self.login_error
            return self._issue(external_id)

    def refresh_token(self, refresh_token: str) -> Tuple[str, str, datetime]:
        """Rotate a refresh token."""
        with self._guard:
            self.refreshes += 1
            if self.refresh_error is not None:
                raise self.refresh_error
            return self._issue(self.subjects[refresh_token])

    def close(self) -> None:
        """Duck-typed close."""
        self.closed = True


class SharedStore(InMemoryTokenStore):
    """In-memory store that claims to be visible to other processes."""

    shared = True


class RecordingLogger:
    """Stand-in for the module's loguru logger, keeping the formatted messages for assertions."""

    def __init__(self, warnings: List[str]) -> None:
        self.warnings: List[str] = warnings

    def warning(self, message: str, *args) -> None:
        """Record a warning."""
        self.warnings.append(message.format(*args))

    def info(self, message: str, *args) -> None:
        """Ignore the informational messages the broker also emits."""


class ExplodingCloseStore(InMemoryTokenStore):
    """In-memory store whose duck-typed ``close`` raises something other than ``TokenStoreUnavailable``."""

    def __init__(self, error: Exception) -> None:
        super().__init__()
        self.error: Exception = error
        self.close_calls: int = 0

    def close(self) -> None:
        """Fail the way a caller-supplied component with its own pool might."""
        self.close_calls += 1
        raise self.error


class ClosingStore(InMemoryTokenStore):
    """In-memory store exposing a duck-typed ``close``."""

    def __init__(self) -> None:
        super().__init__()
        self.closed: bool = False

    def close(self) -> None:
        """Duck-typed close."""
        self.closed = True


class RaisingStore(InMemoryTokenStore):
    """Store whose selected operations report an unreachable backend."""

    def __init__(self, failing: Tuple[str, ...] = ("get", "set", "delete")) -> None:
        super().__init__()
        self.failing: Tuple[str, ...] = failing

    def _check(self, operation: str) -> None:
        if operation in self.failing:
            raise TokenStoreUnavailable(f"backend down on {operation}")

    def get(self, key: str) -> Optional[bytes]:
        self._check("get")
        return super().get(key)

    def set(self, key: str, value: bytes, ttl: float) -> None:
        self._check("set")
        super().set(key, value, ttl)

    def delete(self, key: str) -> None:
        self._check("delete")
        super().delete(key)


class RecordingLock:
    """Lock that counts every request and either always grants or never does."""

    def __init__(self, grants: bool = True) -> None:
        self.grants: bool = grants
        self.acquire_calls: int = 0
        self.release_calls: int = 0

    def acquire(self, key: str, ttl: float) -> bool:
        """Grant or refuse, as configured."""
        self.acquire_calls += 1
        return self.grants

    def release(self, key: str) -> None:
        """Release."""
        self.release_calls += 1


class RaisingLock(RecordingLock):
    """Lock whose selected operations report an unreachable backend."""

    def __init__(self, failing: Tuple[str, ...] = ("acquire", "release"), grants: bool = True) -> None:
        super().__init__(grants=grants)
        self.failing: Tuple[str, ...] = failing

    def acquire(self, key: str, ttl: float) -> bool:
        """Refuse to answer, or answer as configured."""
        self.acquire_calls += 1
        if "acquire" in self.failing:
            raise TokenStoreUnavailable("lock backend down on acquire")
        return self.grants

    def release(self, key: str) -> None:
        """Refuse to answer, or record the release."""
        self.release_calls += 1
        if "release" in self.failing:
            raise TokenStoreUnavailable("lock backend down on release")


class HolderWritesLock(RecordingLock):
    """A lock somebody else holds, who finishes their write before we re-read the cache."""

    def __init__(self, store: InMemoryTokenStore, key: str, value: bytes) -> None:
        super().__init__(grants=False)
        self._store = store
        self._key = key
        self._value = value

    def acquire(self, key: str, ttl: float) -> bool:
        """Refuse the lock, having written what the holder would have written."""
        self._store.set(self._key, self._value, 3600.0)
        return super().acquire(key, ttl)


class SpyLimiter:
    """Limiter recording every acquire."""

    def __init__(self) -> None:
        self.acquisitions: int = 0

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Grant immediately."""
        self.acquisitions += 1
        return True


def keys_for(external_user_id: str, issuer: str = ISSUER, tenant: str = TENANT_ID) -> Tuple[str, str, str]:
    """The three store keys the broker is expected to use."""
    session_id = TimedSession._session_id_(issuer, tenant, external_user_id)
    return f"pks:{session_id}:a", f"pks:{session_id}:r", f"pks:{session_id}:lk"


def make_broker(client: Optional[FakeClient] = None, store=None, **kwargs) -> Tuple[TokenBroker, FakeClient]:
    """Build a broker with a fake client and deterministic (jitter-free) refresh thresholds."""
    client = client or FakeClient()
    kwargs.setdefault("early_refresh_jitter_seconds", 0.0)
    kwargs.setdefault("lock_wait_seconds", 0.0)
    broker = TokenBroker(
        SERVICE_URL,
        TENANT_API_KEY,
        store=store if store is not None else InMemoryTokenStore(),
        client=client,
        **kwargs,
    )
    return broker, client


def test_first_call_logs_in_and_caches():
    store = InMemoryTokenStore()
    broker, client = make_broker(store=store)

    token = broker.token_for(USER)

    assert client.logins == 1
    assert claims_of(token)["ext-sub"] == USER
    key_a, key_r, _ = keys_for(USER)
    assert store.get(key_a) is not None
    assert store.get(key_r) is not None


def test_second_call_is_served_from_cache():
    broker, client = make_broker()

    first = broker.token_for(USER)
    second = broker.token_for(USER)

    assert second == first
    assert client.logins == 1, "a cached token must not trigger a second login"
    assert client.refreshes == 0
    assert broker.stats().hits == 1


def test_bootstrap_learns_realm_from_the_first_jwt():
    store = InMemoryTokenStore()
    broker, _ = make_broker(store=store)

    broker.token_for(USER)

    key_from_jwt, _, _ = keys_for(USER, issuer=ISSUER, tenant=TENANT_ID)
    key_from_config, _, _ = keys_for(USER, issuer=SERVICE_URL, tenant=TENANT_API_KEY)
    assert store.get(key_from_jwt) is not None
    assert store.get(key_from_config) is None


def test_keys_match_timed_session_session_id():
    store = InMemoryTokenStore()
    broker, _ = make_broker(store=store)

    token = broker.token_for(USER)

    assert store.get(f"pks:{TimedSession.extract_session_id(token)}:a") is not None


def test_external_user_id_is_absent_from_store_keys():
    store = InMemoryTokenStore()
    broker, _ = make_broker(store=store)

    broker.token_for(USER)

    cached_keys = list(store._data)
    assert cached_keys, "nothing was cached, so the assertion below would be vacuous"
    assert all(USER not in key for key in cached_keys)


def test_token_near_expiry_is_refreshed_not_relogged():
    broker, client = make_broker(client=FakeClient(lifetime=310.0), early_refresh_seconds=600.0)

    first = broker.token_for(USER)
    second = broker.token_for(USER)

    assert client.refreshes == 1
    assert client.logins == 1, "the refresh token must be used instead of a second login"
    assert second != first


def test_refresh_failure_falls_back_to_login():
    client = FakeClient(lifetime=310.0)
    broker, _ = make_broker(client=client, early_refresh_seconds=600.0)
    broker.token_for(USER)
    client.refresh_error = WacomServiceException("Refresh token is invalid.")

    token = broker.token_for(USER)

    assert client.refreshes == 1
    assert client.logins == 2
    assert claims_of(token)["ext-sub"] == USER
    assert broker.stats().refresh_failures == 1


def test_refresh_rejection_drops_the_refresh_key():
    store = InMemoryTokenStore()
    client = FakeClient(lifetime=310.0)
    broker, _ = make_broker(client=client, store=store, early_refresh_seconds=600.0)
    broker.token_for(USER)
    _, key_r, _ = keys_for(USER)
    rejected = store.get(key_r)
    assert rejected is not None
    client.refresh_error = WacomServiceException("Refresh token is invalid.")
    client.lifetime = 3600.0

    broker.token_for(USER)

    kept = store.get(key_r)
    assert kept is not None, "the login that followed the rejection must have written a fresh refresh token"
    assert kept != rejected, "the rejected refresh token must not survive in the cache"


def test_rejected_refresh_token_is_dropped_even_when_the_fallback_login_fails():
    """The drop has to happen at the rejection, not as a side effect of the login that usually follows it.

    When the fallback login succeeds it overwrites ``:r`` anyway; only a failing login shows whether the rejected
    token was really dropped, which is also the case that matters - it must not be left for the next request to
    retry.
    """
    store = InMemoryTokenStore()
    client = FakeClient(lifetime=310.0)
    broker, _ = make_broker(client=client, store=store, early_refresh_seconds=600.0)
    broker.token_for(USER)
    _, key_r, _ = keys_for(USER)
    assert store.get(key_r) is not None
    client.refresh_error = WacomServiceException("Refresh token is invalid.")
    client.login_error = WacomServiceException("Login failed.")

    with pytest.raises(WacomServiceException, match="Login failed."):
        broker.token_for(USER)

    assert store.get(key_r) is None, "a rejected refresh token must not survive a failed fallback login"


def test_expired_cache_entry_is_a_miss():
    """Review focus: a cached token whose expiry has already passed is never handed out.

    The store entry is still live - this is the pod that slept through its token's lifetime, or whose clock moved -
    so only the broker's own check of ``expires_at`` stands between the caller and a dead token.
    """
    store = InMemoryTokenStore()
    broker, client = make_broker(store=store, early_refresh_seconds=0.0)
    live = broker.token_for(USER)
    key_a, _, _ = keys_for(USER)
    store.set(key_a, forge(live, time.time() + 600.0), 600.0)

    assert broker.token_for(USER) == live, "control: a hand-built entry with a future expiry is served as a hit"
    assert client.logins == 1 and client.refreshes == 0

    stale = mint(USER, ttl=-5.0)
    store.set(key_a, forge(stale, time.time() - 5.0), 600.0)

    token = broker.token_for(USER)

    assert token != stale
    assert claims_of(token)["exp"] > time.time()
    assert client.refreshes == 1
    assert broker.stats().misses == 2


def test_undecryptable_value_is_a_miss():
    """Review focus: foreign bytes in the store degrade to a miss instead of raising."""
    store = InMemoryTokenStore()
    cipher = AesGcmCipher("k1", b"\x01" * 32)
    broker, client = make_broker(store=store, cipher=cipher)
    broker.token_for(USER)
    key_a, _, _ = keys_for(USER)
    store.set(key_a, b"this-is-not-a-ciphertext", 600.0)

    token = broker.token_for(USER)

    assert claims_of(token)["ext-sub"] == USER
    assert client.refreshes == 1, "the corrupt access entry is a miss, but the refresh token is still usable"
    assert broker.stats().misses == 2


def test_value_moved_to_another_users_key_is_a_miss():
    """A ciphertext copied onto another user's key must not authenticate that user."""
    store = InMemoryTokenStore()
    cipher = AesGcmCipher("k1", b"\x02" * 32)
    broker, _ = make_broker(store=store, cipher=cipher)
    victim_token = broker.token_for(USER)
    broker.token_for(OTHER_USER)
    victim_key, _, _ = keys_for(USER)
    attacker_key, _, _ = keys_for(OTHER_USER)
    stolen = store.get(victim_key)
    assert stolen is not None
    store.set(attacker_key, stolen, 600.0)

    token = broker.token_for(OTHER_USER)

    assert token != victim_token
    assert claims_of(token)["ext-sub"] == OTHER_USER


def test_concurrent_first_call_logs_in_once():
    """Review focus: a cold start under concurrency costs exactly one login.

    The fake login is slow enough that every thread would be inside it at once if the bootstrap were unguarded, so
    the single login counted here is the broker serialising them, not the threads failing to overlap.
    """
    thread_count = 8
    broker, client = make_broker(client=FakeClient(login_delay=0.05))
    barrier = threading.Barrier(thread_count)
    results: List[str] = []
    errors: List[BaseException] = []
    guard = threading.Lock()

    def worker() -> None:
        try:
            barrier.wait(timeout=5.0)
            token = broker.token_for(USER)
            with guard:
                results.append(token)
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            with guard:
                errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(thread_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10.0)

    assert not errors, f"worker threads raised: {errors}"
    assert len(results) == thread_count
    assert client.logins == 1
    assert len(set(results)) == 1, "every caller must see the same token"


def test_lost_lock_falls_back_to_login_without_blocking():
    lock = RecordingLock(grants=False)
    broker, client = make_broker(lock=lock)
    broker.token_for(USER)
    broker.invalidate(USER, drop_refresh=True)

    token = broker.token_for(USER)

    assert claims_of(token)["ext-sub"] == USER
    assert client.logins == 2
    assert lock.acquire_calls == 1, "a lost lock must not be retried in a loop"
    assert broker.stats().lock_contentions == 1


def test_lock_loser_is_served_by_the_holders_write():
    """The branch that justifies ``lock_wait_seconds``: a contended renewal costs zero extra PKS calls."""
    store = InMemoryTokenStore()
    key_a, _, _ = keys_for(USER)
    planted = mint(USER, ttl=3600.0)
    lock = HolderWritesLock(store, key_a, forge(planted, time.time() + 3600.0))
    broker, client = make_broker(store=store, lock=lock, lock_wait_seconds=0.05)
    broker.token_for(USER)  # bootstrap; the lock is not used here
    broker.invalidate(USER)  # so the next call misses, contends, and waits for the holder
    before = broker.stats()

    token = broker.token_for(USER)

    assert token == planted, "the holder's write must be used rather than a token of our own"
    assert client.logins == 1
    assert client.refreshes == 0
    assert broker.stats().hits == before.hits, "the call already counted a miss; it must not also count a hit"
    assert broker.stats().misses == before.misses + 1
    assert broker.stats().lock_contentions == before.lock_contentions + 1


def test_renewal_releases_the_lock_it_took():
    lock = RecordingLock()
    broker, _ = make_broker(lock=lock)
    broker.token_for(USER)
    broker.invalidate(USER)

    broker.token_for(USER)

    assert lock.acquire_calls == 1
    assert lock.release_calls == 1


def test_renewal_that_outlived_the_lock_ttl_does_not_release_it():
    """``TokenLock.release`` is not owner-aware, so a lapsed holder releasing would free somebody else's lock."""
    lock = RecordingLock()
    broker, _ = make_broker(lock=lock, lock_ttl_seconds=0.0)
    broker.token_for(USER)
    broker.invalidate(USER)

    broker.token_for(USER)

    assert lock.acquire_calls == 1
    assert lock.release_calls == 0


def test_an_unreachable_store_degrades_to_a_login_per_call():
    """Every store call - get, set and delete - is unreachable, and no request fails because of it."""
    store = RaisingStore(failing=("get", "set", "delete"))
    broker, client = make_broker(store=store)

    first = broker.token_for(USER)
    broker.invalidate(USER, drop_refresh=True)
    second = broker.token_for(USER)

    assert claims_of(first)["ext-sub"] == USER
    assert claims_of(second)["ext-sub"] == USER
    assert client.logins == 2, "nothing can be cached, so every call logs in"
    assert broker.stats().misses == 2


def test_an_unreachable_lock_backend_renews_without_waiting_for_a_holder():
    """A lock nobody can reach has no holder, so waiting ``lock_wait_seconds`` for one would be pure latency."""
    lock = RaisingLock(failing=("acquire", "release"))
    client = FakeClient(lifetime=310.0)
    broker, _ = make_broker(client=client, lock=lock, early_refresh_seconds=600.0, lock_wait_seconds=30.0)
    broker.token_for(USER)

    started = time.monotonic()
    token = broker.token_for(USER)
    elapsed = time.monotonic() - started

    assert claims_of(token)["ext-sub"] == USER
    assert elapsed < 1.0, f"waited {elapsed:.2f}s for a holder that cannot exist"
    assert lock.release_calls == 0, "a lock that was never taken must not be released"
    assert broker.stats().lock_contentions == 0, "an outage must not be reported as contention"
    assert client.refreshes == 1, "the renewal still takes the refresh path, it just skips the lock"
    assert client.logins == 1


def test_a_failing_lock_release_does_not_fail_the_request():
    lock = RaisingLock(failing=("release",), grants=True)
    broker, client = make_broker(lock=lock)
    broker.token_for(USER)
    broker.invalidate(USER, drop_refresh=True)

    token = broker.token_for(USER)

    assert claims_of(token)["ext-sub"] == USER
    assert lock.release_calls == 1, "the release was attempted and its failure swallowed"
    assert client.logins == 2


def test_invalidate_drops_access_key_only_by_default():
    store = InMemoryTokenStore()
    broker, client = make_broker(store=store)
    broker.token_for(USER)
    key_a, key_r, _ = keys_for(USER)

    broker.invalidate(USER)

    assert store.get(key_a) is None
    assert store.get(key_r) is not None
    broker.token_for(USER)
    assert client.refreshes == 1, "the kept refresh token must be used instead of a login"
    assert client.logins == 1


def test_invalidate_with_drop_refresh_drops_both():
    store = InMemoryTokenStore()
    broker, client = make_broker(store=store)
    broker.token_for(USER)
    key_a, key_r, _ = keys_for(USER)

    broker.invalidate(USER, drop_refresh=True)

    assert store.get(key_a) is None
    assert store.get(key_r) is None
    broker.token_for(USER)
    assert client.logins == 2
    assert client.refreshes == 0


def test_paced_call_consumes_a_limiter_token():
    broker, _ = make_broker(rate_limit=7.0)
    assert isinstance(broker._limiter, TokenBucketLimiter)
    assert broker._limiter.rate == 7.0
    spy = SpyLimiter()
    broker._limiter = spy

    broker.token_for(USER, paced=True)

    assert spy.acquisitions == 1


def test_unpaced_call_ignores_the_limiter():
    broker, _ = make_broker(rate_limit=7.0)
    spy = SpyLimiter()
    broker._limiter = spy

    broker.token_for(USER)

    assert spy.acquisitions == 0


def test_pacing_without_a_rate_limit_is_a_no_op():
    broker, client = make_broker()

    broker.token_for(USER, paced=True)

    assert client.logins == 1


def test_shared_store_without_cipher_is_rejected():
    with pytest.raises(ValueError, match="shared token store requires a cipher"):
        TokenBroker(SERVICE_URL, TENANT_API_KEY, store=SharedStore(), client=FakeClient())

    with pytest.raises(ValueError, match="shared token store requires a cipher"):
        TokenBroker(SERVICE_URL, TENANT_API_KEY, store=SharedStore(), cipher=NullCipher(), client=FakeClient())


def test_shared_store_with_a_real_cipher_is_accepted():
    broker, client = make_broker(store=SharedStore(), cipher=AesGcmCipher("k1", b"\x03" * 32))

    assert claims_of(broker.token_for(USER))["ext-sub"] == USER
    assert client.logins == 1


def test_the_jitter_offset_is_stable_per_user_and_spread_across_users():
    """The offset must not be redrawn per read, or a user read many times a second renews at the band's edge."""
    jitter = 120.0
    broker, _ = make_broker(early_refresh_jitter_seconds=jitter)
    key_a, _, _ = keys_for(USER)

    assert broker._jitter_for(key_a) == broker._jitter_for(key_a), "the offset must be constant across reads"

    offsets = [broker._jitter_for(f"pks:{index:064x}:a") for index in range(200)]
    assert all(0.0 <= offset < jitter for offset in offsets)
    assert len(set(offsets)) > 190, "near-distinct offsets, not one shared value"
    assert min(offsets) < jitter * 0.2 and max(offsets) > jitter * 0.8, "the whole band is used"


def test_zero_jitter_means_no_offset():
    broker, _ = make_broker(early_refresh_jitter_seconds=0.0)

    assert broker._jitter_for(keys_for(USER)[0]) == 0.0


def test_the_jitter_offset_widens_the_early_refresh_window():
    jitter = 120.0
    probe, _ = make_broker(early_refresh_jitter_seconds=jitter)
    offset = probe._jitter_for(keys_for(USER)[0])
    assert offset > 1.0, f"this user's offset ({offset:.1f}s) is too small to tell the two cases apart"

    outside, outside_client = make_broker(
        client=FakeClient(lifetime=300.0 + offset + 30.0),
        early_refresh_seconds=300.0,
        early_refresh_jitter_seconds=jitter,
    )
    first = outside.token_for(USER)

    assert outside.token_for(USER) == first, "life beyond the offset threshold is still a hit"
    assert outside_client.refreshes == 0

    inside, inside_client = make_broker(
        client=FakeClient(lifetime=300.0 + offset - 30.0),
        early_refresh_seconds=300.0,
        early_refresh_jitter_seconds=jitter,
    )
    inside.token_for(USER)
    inside.token_for(USER)

    assert inside_client.refreshes == 1, "life inside the offset threshold is renewed, so the offset is applied"


def test_stats_counts_hits_misses_logins_refreshes():
    broker, _ = make_broker()
    broker.token_for(USER)
    broker.token_for(USER)
    broker.invalidate(USER)
    broker.token_for(USER)

    assert broker.stats() == BrokerStats(
        hits=1, misses=2, logins=1, refreshes=1, refresh_failures=0, lock_contentions=0
    )


def test_importing_the_broker_does_not_import_redis():
    code = (
        "import sys, knowledge.services.broker;"
        "sys.exit(1 if 'redis' in sys.modules or 'knowledge.services.cache.redis' in sys.modules else 0)"
    )
    assert subprocess.run([sys.executable, "-c", code], check=False).returncode == 0


def test_context_manager_closes_the_store():
    store = ClosingStore()
    client = FakeClient()
    lock = InProcessLock()  # no close(): the broker must not require one

    with TokenBroker(SERVICE_URL, TENANT_API_KEY, store=store, lock=lock, client=client) as broker:
        assert broker.token_for(USER)

    assert store.closed
    assert not client.closed, "an injected client belongs to the caller, not to the broker"


def test_close_leaves_an_injected_client_alone():
    """The spec gives the caller ownership of an injected client: its timeouts, its retries, its lifetime."""
    broker, client = make_broker()
    broker.token_for(USER)

    broker.close()

    assert not client.closed, "closing an injected client would release a session the caller may still be using"


def test_close_closes_a_client_the_broker_built_itself(monkeypatch):
    """The other half of the rule: nobody else can release a client the broker constructed, so the broker must."""
    built = FakeClient()
    monkeypatch.setattr(broker_module, "WacomServiceAPIClient", lambda service_url: built)
    broker = TokenBroker(SERVICE_URL, TENANT_API_KEY, store=InMemoryTokenStore())
    assert broker._client is built  # pylint: disable=protected-access

    broker.close()

    assert built.closed


def test_close_releases_every_component_even_when_one_raises(monkeypatch):
    """A caller-supplied component whose close raises must not strand the ones after it, nor reach the caller."""
    warnings: List[str] = []
    monkeypatch.setattr(broker_module, "logger", RecordingLogger(warnings))
    store = ExplodingCloseStore(RuntimeError("the store's own pool is already gone"))
    built = FakeClient()
    monkeypatch.setattr(broker_module, "WacomServiceAPIClient", lambda service_url: built)
    broker = TokenBroker(SERVICE_URL, TENANT_API_KEY, store=store)

    broker.close()  # must not raise: an ASGI lifespan shutdown would fail with it

    assert store.close_calls == 1
    assert built.closed, "the client after the failing component must still be released"
    assert any("ExplodingCloseStore" in message and "already gone" in message for message in warnings), warnings


def test_a_shared_store_with_the_default_lock_warns(monkeypatch):
    """Foot-gun 1: every process then believes it holds the renewal lock for every user."""
    warnings: List[str] = []
    monkeypatch.setattr(broker_module, "logger", RecordingLogger(warnings))

    TokenBroker(
        SERVICE_URL, TENANT_API_KEY, store=SharedStore(), cipher=AesGcmCipher("k1", b"\x04" * 32), client=FakeClient()
    )

    assert len(warnings) == 1, warnings
    assert "process-local lock" in warnings[0]
    assert "InProcessLock" in warnings[0]


def test_a_shared_store_with_an_explicit_process_local_lock_warns(monkeypatch):
    """Passing the process-local lock by hand is the same mistake as letting it default."""
    warnings: List[str] = []
    monkeypatch.setattr(broker_module, "logger", RecordingLogger(warnings))

    TokenBroker(
        SERVICE_URL,
        TENANT_API_KEY,
        store=SharedStore(),
        cipher=AesGcmCipher("k1", b"\x04" * 32),
        lock=InProcessLock(),
        client=FakeClient(),
    )

    assert len(warnings) == 1, warnings
    assert "process-local lock" in warnings[0]


def test_a_shared_store_with_a_custom_lock_is_not_warned_about(monkeypatch):
    """A shared lock of the caller's own is legitimate, so this must stay a warning about *process-local* locks."""
    warnings: List[str] = []
    monkeypatch.setattr(broker_module, "logger", RecordingLogger(warnings))

    TokenBroker(
        SERVICE_URL,
        TENANT_API_KEY,
        store=SharedStore(),
        cipher=AesGcmCipher("k1", b"\x04" * 32),
        lock=RecordingLock(),
        client=FakeClient(),
    )

    assert warnings == []


def test_a_process_local_store_with_the_default_lock_is_not_warned_about(monkeypatch):
    """The defaults are right for a single process; warning about them would train operators to ignore the log."""
    warnings: List[str] = []
    monkeypatch.setattr(broker_module, "logger", RecordingLogger(warnings))

    make_broker()

    assert warnings == []
