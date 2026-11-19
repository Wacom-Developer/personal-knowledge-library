# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the tiered token store; no Redis, no network, no sleeping."""

import subprocess
import sys
from typing import Dict, List, Optional, Tuple

import pytest

from knowledge.services.cache.base import TokenStoreUnavailable
from knowledge.services.cache.memory import InMemoryTokenStore
from knowledge.services.cache.tiered import AsyncTieredTokenStore, TieredTokenStore


class Clock:
    """Manual monotonic clock."""

    def __init__(self) -> None:
        self.now: float = 1000.0

    def __call__(self) -> float:
        return self.now


class SpyStore(InMemoryTokenStore):
    """In-memory store recording calls; optionally raises TokenStoreUnavailable on every call."""

    def __init__(self, clock: Clock, shared: bool = False, failing: bool = False) -> None:
        super().__init__(clock=clock)
        self.shared = shared
        self.failing = failing
        self.calls: List[str] = []

    def _enter(self, name: str) -> None:
        self.calls.append(name)
        if self.failing:
            raise TokenStoreUnavailable("backend down")

    def get(self, key: str) -> Optional[bytes]:
        self._enter("get")
        return super().get(key)

    def set(self, key: str, value: bytes, ttl: float) -> None:
        self._enter("set")
        super().set(key, value, ttl)

    def delete(self, key: str) -> None:
        self._enter("delete")
        super().delete(key)

    def ttl(self, key: str) -> Optional[float]:
        self._enter("ttl")
        return super().ttl(key)


class NoExpiryL2(SpyStore):
    """L2 that holds values but reports no TTL for them."""

    def ttl(self, key: str) -> Optional[float]:
        self.calls.append("ttl")
        return None


class TtlFailingL2(SpyStore):
    """L2 whose get works but whose ttl raises."""

    def ttl(self, key: str) -> Optional[float]:
        self.calls.append("ttl")
        raise TokenStoreUnavailable("backend down")


class AsyncSpyStore:
    """Async dict-backed store with a manual clock, recording calls."""

    def __init__(self, clock: Clock, shared: bool = False, failing: bool = False) -> None:
        self.shared = shared
        self.failing = failing
        self.calls: List[str] = []
        self._clock = clock
        self._data: Dict[str, Tuple[bytes, float]] = {}

    def _enter(self, name: str) -> None:
        self.calls.append(name)
        if self.failing:
            raise TokenStoreUnavailable("backend down")

    async def get(self, key: str) -> Optional[bytes]:
        self._enter("get")
        entry = self._data.get(key)
        return entry[0] if entry and entry[1] > self._clock() else None

    async def set(self, key: str, value: bytes, ttl: float) -> None:
        self._enter("set")
        self._data[key] = (value, self._clock() + ttl)

    async def delete(self, key: str) -> None:
        self._enter("delete")
        self._data.pop(key, None)

    async def ttl(self, key: str) -> Optional[float]:
        self._enter("ttl")
        entry = self._data.get(key)
        return entry[1] - self._clock() if entry and entry[1] > self._clock() else None


class AsyncNoExpiryL2(AsyncSpyStore):
    """Async L2 that holds values but reports no TTL for them."""

    async def ttl(self, key: str) -> Optional[float]:
        self.calls.append("ttl")
        return None


def make(failing_l2: bool = False, l1_shared: bool = False, l2_shared: bool = True):
    clock = Clock()
    l1 = SpyStore(clock, shared=l1_shared)
    l2 = SpyStore(clock, shared=l2_shared, failing=failing_l2)
    return clock, l1, l2, TieredTokenStore(l1, l2)


def test_get_prefers_l1():
    _, l1, l2, tiered = make()
    l1.set("k", b"from-l1", 60)
    l2.set("k", b"from-l2", 60)
    l2.calls.clear()
    assert tiered.get("k") == b"from-l1"
    assert l2.calls == []


def test_l1_miss_falls_through_and_backfills_l1():
    _, l1, l2, tiered = make()
    l2.set("k", b"v", 60)
    assert l1.get("k") is None
    assert tiered.get("k") == b"v"
    assert l1.get("k") == b"v"


def test_backfill_uses_remaining_l2_ttl_so_entry_never_outlives_token():
    clock, l1, l2, tiered = make()
    l2.set("k", b"v", 60)
    clock.now += 50  # 10s left in L2
    assert tiered.get("k") == b"v"
    assert l1.ttl("k") == pytest.approx(10)
    clock.now += 11
    assert l1.get("k") is None


def test_no_backfill_when_l2_reports_no_ttl():
    clock = Clock()
    l1 = SpyStore(clock)
    l2 = NoExpiryL2(clock, shared=True)
    l2.set("k", b"v", 60)
    tiered = TieredTokenStore(l1, l2)
    assert tiered.get("k") == b"v"
    assert l1.get("k") is None


def test_l2_ttl_failure_after_hit_skips_backfill_but_returns_value():
    clock = Clock()
    l1 = SpyStore(clock)
    l2 = TtlFailingL2(clock, shared=True)
    l2.set("k", b"v", 60)
    tiered = TieredTokenStore(l1, l2)
    assert tiered.get("k") == b"v"
    assert l2.calls[-1] == "ttl"
    assert l1.get("k") is None


def test_miss_in_both_tiers_returns_none_without_backfill():
    _, l1, _, tiered = make()
    assert tiered.get("k") is None
    assert "set" not in l1.calls


def test_set_writes_both_tiers():
    _, l1, l2, tiered = make()
    tiered.set("k", b"v", 60)
    assert l1.get("k") == b"v"
    assert l2.get("k") == b"v"
    assert l2.ttl("k") == pytest.approx(60)


def test_delete_removes_from_both_tiers():
    _, l1, l2, tiered = make()
    tiered.set("k", b"v", 60)
    tiered.delete("k")
    assert l1.get("k") is None
    assert l2.get("k") is None


def test_l2_failure_still_serves_from_l1():
    _, l1, l2, tiered = make(failing_l2=True)
    l1.set("k", b"v", 60)
    assert tiered.get("k") == b"v"
    assert l2.calls == []


def test_l2_failure_on_l1_miss_returns_none():
    _, _, l2, tiered = make(failing_l2=True)
    assert tiered.get("k") is None
    assert l2.calls == ["get"]


def test_l2_failure_on_set_does_not_raise_and_l1_is_written():
    _, l1, l2, tiered = make(failing_l2=True)
    tiered.set("k", b"v", 60)
    assert l2.calls == ["set"]
    assert l1.get("k") == b"v"
    assert tiered.get("k") == b"v"


def test_l2_failure_on_delete_still_clears_l1():
    _, l1, l2, tiered = make(failing_l2=True)
    l1.set("k", b"v", 60)
    tiered.delete("k")
    assert l2.calls == ["delete"]
    assert l1.get("k") is None


def test_ttl_prefers_l1_then_l2():
    _, l1, l2, tiered = make()
    l2.set("k", b"v", 60)
    assert tiered.ttl("k") == pytest.approx(60)
    l1.set("k", b"v", 30)
    l2.calls.clear()
    assert tiered.ttl("k") == pytest.approx(30)
    assert l2.calls == []


def test_ttl_with_l2_down_and_l1_miss_is_none():
    _, _, _, tiered = make(failing_l2=True)
    assert tiered.ttl("k") is None


def test_l2_failure_is_logged_as_warning(monkeypatch):
    from knowledge.services.cache import tiered as module

    warnings: List[str] = []

    class FakeLogger:
        def warning(self, message: str, *args) -> None:
            warnings.append(message.format(*args))

    monkeypatch.setattr(module, "logger", FakeLogger())
    _, _, _, tiered = make(failing_l2=True)
    tiered.set("k", b"v", 60)
    assert len(warnings) == 1
    assert "backend down" in warnings[0]


@pytest.mark.parametrize(
    "l1_shared, l2_shared, expected",
    [(False, False, False), (True, False, True), (False, True, True), (True, True, True)],
)
def test_shared_is_true_when_either_tier_is_shared(l1_shared, l2_shared, expected):
    _, _, _, tiered = make(l1_shared=l1_shared, l2_shared=l2_shared)
    assert tiered.shared is expected


def test_tiered_module_does_not_import_redis_backend():
    code = (
        "import sys, knowledge.services.cache, knowledge.services.cache.tiered;"
        "sys.exit(1 if 'knowledge.services.cache.redis' in sys.modules else 0)"
    )
    assert subprocess.run([sys.executable, "-c", code], check=False).returncode == 0


# ---- async ----------------------------------------------------------------------------------------------------


def amake(failing_l2: bool = False, l1_shared: bool = False, l2_shared: bool = True):
    clock = Clock()
    l1 = AsyncSpyStore(clock, shared=l1_shared)
    l2 = AsyncSpyStore(clock, shared=l2_shared, failing=failing_l2)
    return clock, l1, l2, AsyncTieredTokenStore(l1, l2)


async def test_async_get_prefers_l1():
    _, l1, l2, tiered = amake()
    await l1.set("k", b"from-l1", 60)
    await l2.set("k", b"from-l2", 60)
    l2.calls.clear()
    assert await tiered.get("k") == b"from-l1"
    assert l2.calls == []


async def test_async_l1_miss_falls_through_and_backfills_with_remaining_ttl():
    clock, l1, l2, tiered = amake()
    await l2.set("k", b"v", 60)
    clock.now += 50
    assert await tiered.get("k") == b"v"
    assert await l1.ttl("k") == pytest.approx(10)


async def test_async_no_backfill_when_l2_reports_no_ttl():
    clock = Clock()
    l1 = AsyncSpyStore(clock)
    l2 = AsyncNoExpiryL2(clock, shared=True)
    await l2.set("k", b"v", 60)
    tiered = AsyncTieredTokenStore(l1, l2)
    assert await tiered.get("k") == b"v"
    assert await l1.get("k") is None


async def test_async_set_and_delete_hit_both_tiers():
    _, l1, l2, tiered = amake()
    await tiered.set("k", b"v", 60)
    assert await l1.get("k") == b"v"
    assert await l2.get("k") == b"v"
    await tiered.delete("k")
    assert await l1.get("k") is None
    assert await l2.get("k") is None


async def test_async_l2_failure_still_serves_from_l1():
    _, l1, l2, tiered = amake(failing_l2=True)
    await l1.set("k", b"v", 60)
    assert await tiered.get("k") == b"v"
    assert l2.calls == []


async def test_async_l2_failure_on_set_and_delete_does_not_raise():
    _, l1, l2, tiered = amake(failing_l2=True)
    await tiered.set("k", b"v", 60)
    assert await l1.get("k") == b"v"
    await tiered.delete("k")
    assert await l1.get("k") is None
    assert l2.calls == ["set", "delete"]


async def test_async_l2_failure_on_l1_miss_returns_none_and_ttl_none():
    _, _, _, tiered = amake(failing_l2=True)
    assert await tiered.get("k") is None
    assert await tiered.ttl("k") is None


async def test_async_ttl_prefers_l1_then_l2():
    _, l1, l2, tiered = amake()
    await l2.set("k", b"v", 60)
    assert await tiered.ttl("k") == pytest.approx(60)
    await l1.set("k", b"v", 30)
    l2.calls.clear()
    assert await tiered.ttl("k") == pytest.approx(30)
    assert l2.calls == []


@pytest.mark.parametrize(
    "l1_shared, l2_shared, expected", [(False, False, False), (True, False, True), (False, True, True)]
)
def test_async_shared_is_true_when_either_tier_is_shared(l1_shared, l2_shared, expected):
    _, _, _, tiered = amake(l1_shared=l1_shared, l2_shared=l2_shared)
    assert tiered.shared is expected
