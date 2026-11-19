# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the Redis token store and lock, driven by hand-written fakes (no Redis, no network)."""

from typing import Any, Dict, List, Optional, Tuple

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from knowledge.services.cache import TokenStoreUnavailable
from knowledge.services.cache.redis import AsyncRedisLock, AsyncRedisTokenStore, RedisLock, RedisTokenStore

# pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument


def assert_guarded_release(eval_calls: List[Tuple[str, int, Tuple[Any, ...]]], key: str, token: str) -> None:
    """Pin the Lua compare-and-delete, which the fake cannot execute.

    The fake compares tokens in Python, so only the recorded ``eval`` call proves the real script is guarded: one key,
    ``(key, token)`` as arguments, and a ``get`` comparison against ARGV[1] occurring before the ``del``.
    """
    assert len(eval_calls) == 1
    script, numkeys, args = eval_calls[0]
    assert numkeys == 1
    assert args == (key, token)
    compare = "redis.call('get', KEYS[1]) == ARGV[1]"
    assert compare in script
    assert "redis.call('del', KEYS[1])" in script
    assert script.index(compare) < script.index("redis.call('del', KEYS[1])")


class FakeRedis:
    """Implements only the client surface the store and lock use. Expiry is recorded, never enforced."""

    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}
        self.px: Dict[str, Optional[int]] = {}
        self.eval_calls: List[Tuple[str, int, Tuple[Any, ...]]] = []

    def get(self, name: str) -> Any:
        return self.data.get(name)

    def set(self, name: str, value: Any, px: Optional[int] = None, nx: bool = False) -> Optional[bool]:
        if nx and name in self.data:
            return None
        self.data[name] = value
        self.px[name] = px
        return True

    def delete(self, *names: str) -> int:
        return sum(1 for n in names if self.data.pop(n, None) is not None)

    def pttl(self, name: str) -> int:
        if name not in self.data:
            return -2
        px = self.px.get(name)
        return -1 if px is None else px

    def eval(self, script: str, numkeys: int, *args: Any) -> int:
        self.eval_calls.append((script, numkeys, args))
        key, token = args[0], args[1]
        if self.data.get(key) == token:
            del self.data[key]
            return 1
        return 0


class FailingRedis:
    """Every method raises a real redis ConnectionError."""

    def _fail(self, *_a: Any, **_k: Any) -> Any:
        raise RedisConnectionError("redis is down")

    get = set = delete = pttl = eval = _fail


class AsyncFakeRedis:
    def __init__(self) -> None:
        self.inner = FakeRedis()

    async def get(self, name: str) -> Any:
        return self.inner.get(name)

    async def set(self, name: str, value: Any, px: Optional[int] = None, nx: bool = False) -> Optional[bool]:
        return self.inner.set(name, value, px=px, nx=nx)

    async def delete(self, *names: str) -> int:
        return self.inner.delete(*names)

    async def pttl(self, name: str) -> int:
        return self.inner.pttl(name)

    async def eval(self, script: str, numkeys: int, *args: Any) -> int:
        return self.inner.eval(script, numkeys, *args)


class AsyncFailingRedis:
    async def _fail(self, *_a: Any, **_k: Any) -> Any:
        raise RedisConnectionError("redis is down")

    get = set = delete = pttl = eval = _fail


def test_store_is_shared():
    assert RedisTokenStore(FakeRedis()).shared is True
    assert AsyncRedisTokenStore(AsyncFakeRedis()).shared is True


def test_set_uses_millisecond_expiry():
    fake = FakeRedis()
    RedisTokenStore(fake).set("k", b"v", 1.5)
    assert fake.data["k"] == b"v"
    assert fake.px["k"] == 1500


def test_set_never_passes_zero_expiry():
    fake = FakeRedis()
    RedisTokenStore(fake).set("k", b"v", 0.0001)
    assert fake.px["k"] == 1


def test_get_returns_none_for_missing_key():
    assert RedisTokenStore(FakeRedis()).get("absent") is None


def test_get_round_trip_and_delete():
    store = RedisTokenStore(FakeRedis())
    store.set("k", b"v", 10)
    assert store.get("k") == b"v"
    store.delete("k")
    assert store.get("k") is None


def test_ttl_converts_milliseconds_to_seconds():
    store = RedisTokenStore(FakeRedis())
    store.set("k", b"v", 2.5)
    assert store.ttl("k") == 2.5


def test_ttl_maps_missing_and_no_expiry_to_none():
    fake = FakeRedis()
    store = RedisTokenStore(fake)
    assert store.ttl("absent") is None  # PTTL -2
    fake.data["forever"] = b"v"
    assert store.ttl("forever") is None  # PTTL -1


@pytest.mark.parametrize(
    "call",
    [
        lambda s: s.get("k"),
        lambda s: s.set("k", b"v", 1),
        lambda s: s.delete("k"),
        lambda s: s.ttl("k"),
    ],
)
def test_backend_failure_raises_token_store_unavailable(call):
    with pytest.raises(TokenStoreUnavailable, match="redis is down") as info:
        call(RedisTokenStore(FailingRedis()))
    assert isinstance(info.value.__cause__, RedisConnectionError)


def test_os_error_is_also_mapped():
    class Broken(FakeRedis):
        def get(self, name: str) -> Any:
            raise OSError("socket closed")

    with pytest.raises(TokenStoreUnavailable, match="socket closed"):
        RedisTokenStore(Broken()).get("k")


def test_unrelated_exceptions_are_not_swallowed():
    class Buggy(FakeRedis):
        def get(self, name: str) -> Any:
            raise KeyError("bug")

    with pytest.raises(KeyError):
        RedisTokenStore(Buggy()).get("k")


def test_lock_acquire_uses_set_nx_with_expiry():
    fake = FakeRedis()
    calls: List[Tuple[str, Any, Optional[int], bool]] = []
    original = fake.set

    def spy(name, value, px=None, nx=False):
        calls.append((name, value, px, nx))
        return original(name, value, px=px, nx=nx)

    fake.set = spy  # type: ignore[method-assign]
    assert RedisLock(fake).acquire("lock:u", 30) is True
    name, token, px, nx = calls[0]
    assert (name, px, nx) == ("lock:u", 30000, True)
    assert isinstance(token, str) and len(token) >= 16


def test_lock_acquire_returns_false_when_key_present():
    fake = FakeRedis()
    fake.data["lock:u"] = "someone-else"
    assert RedisLock(fake).acquire("lock:u", 30) is False


def test_lock_release_deletes_own_lock():
    fake = FakeRedis()
    lock = RedisLock(fake)
    assert lock.acquire("lock:u", 30)
    token = fake.data["lock:u"]
    lock.release("lock:u")
    assert "lock:u" not in fake.data
    assert_guarded_release(fake.eval_calls, "lock:u", token)
    assert lock.acquire("lock:u", 30) is True  # tracking cleared, can be taken again


def test_lock_release_only_deletes_own_token():
    fake = FakeRedis()
    first = RedisLock(fake)
    assert first.acquire("lock:u", 30)
    first_token = fake.data["lock:u"]
    # first holder's TTL lapses; a second holder acquires the same key
    del fake.data["lock:u"]
    second = RedisLock(fake)
    assert second.acquire("lock:u", 30)
    holder = fake.data["lock:u"]
    assert holder != first_token

    first.release("lock:u")

    assert fake.data["lock:u"] == holder  # second holder's lock survives
    # the stale holder sent its own token, not the current holder's
    assert_guarded_release(fake.eval_calls, "lock:u", first_token)
    fake.eval_calls.clear()
    second.release("lock:u")
    assert "lock:u" not in fake.data
    assert_guarded_release(fake.eval_calls, "lock:u", holder)


def test_lock_release_without_acquire_is_noop():
    fake = FakeRedis()
    fake.data["lock:u"] = "other"
    RedisLock(fake).release("lock:u")
    assert fake.data["lock:u"] == "other"
    assert not fake.eval_calls


def test_lock_backend_failure_raises_token_store_unavailable():
    with pytest.raises(TokenStoreUnavailable, match="redis is down"):
        RedisLock(FailingRedis()).acquire("k", 1)


def test_lock_release_backend_failure_raises_token_store_unavailable():
    fake = FakeRedis()
    lock = RedisLock(fake)
    lock.acquire("k", 1)
    fake.eval = FailingRedis().eval  # type: ignore[method-assign]
    with pytest.raises(TokenStoreUnavailable, match="redis is down"):
        lock.release("k")


async def test_async_store_round_trip():
    fake = AsyncFakeRedis()
    store = AsyncRedisTokenStore(fake)
    assert await store.get("k") is None
    assert await store.ttl("k") is None
    await store.set("k", b"v", 1.5)
    assert fake.inner.px["k"] == 1500
    assert await store.get("k") == b"v"
    assert await store.ttl("k") == 1.5
    await store.delete("k")
    assert await store.get("k") is None


async def test_async_ttl_no_expiry_is_none():
    fake = AsyncFakeRedis()
    fake.inner.data["k"] = b"v"
    assert await AsyncRedisTokenStore(fake).ttl("k") is None


async def test_async_backend_failure_raises_token_store_unavailable():
    store = AsyncRedisTokenStore(AsyncFailingRedis())
    for coro in (store.get("k"), store.set("k", b"v", 1), store.delete("k"), store.ttl("k")):
        with pytest.raises(TokenStoreUnavailable, match="redis is down") as info:
            await coro
        assert isinstance(info.value.__cause__, RedisConnectionError)


async def test_async_lock_acquire_and_release():
    fake = AsyncFakeRedis()
    lock = AsyncRedisLock(fake)
    assert await lock.acquire("lock:u", 30) is True
    assert fake.inner.px["lock:u"] == 30000
    assert await AsyncRedisLock(fake).acquire("lock:u", 30) is False
    token = fake.inner.data["lock:u"]
    await lock.release("lock:u")
    assert "lock:u" not in fake.inner.data
    assert_guarded_release(fake.inner.eval_calls, "lock:u", token)


async def test_async_lock_release_only_deletes_own_token():
    fake = AsyncFakeRedis()
    first = AsyncRedisLock(fake)
    assert await first.acquire("lock:u", 30)
    first_token = fake.inner.data["lock:u"]
    del fake.inner.data["lock:u"]
    second = AsyncRedisLock(fake)
    assert await second.acquire("lock:u", 30)
    holder = fake.inner.data["lock:u"]
    assert holder != first_token
    await first.release("lock:u")
    assert fake.inner.data["lock:u"] == holder
    assert_guarded_release(fake.inner.eval_calls, "lock:u", first_token)
    fake.inner.eval_calls.clear()
    await second.release("lock:u")
    assert "lock:u" not in fake.inner.data
    assert_guarded_release(fake.inner.eval_calls, "lock:u", holder)


async def test_async_lock_backend_failure_raises_token_store_unavailable():
    with pytest.raises(TokenStoreUnavailable, match="redis is down"):
        await AsyncRedisLock(AsyncFailingRedis()).acquire("k", 1)
