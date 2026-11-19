# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the token-bucket limiters; deterministic, never sleeps on the wall clock."""

import asyncio
import threading
from typing import List

import pytest

from knowledge.services.cache.limiter import AsyncTokenBucketLimiter, TokenBucketLimiter


class FakeTime:
    """Fake clock whose fake ``sleep`` advances it and records every requested duration."""

    def __init__(self) -> None:
        self.now: float = 1000.0
        self.slept: List[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds

    async def async_sleep(self, seconds: float) -> None:
        self.sleep(seconds)


def make(rate: float, capacity=None):
    fake = FakeTime()
    return fake, TokenBucketLimiter(rate, capacity, clock=fake.clock, sleep=fake.sleep)


def test_burst_up_to_capacity_is_immediate():
    fake, limiter = make(rate=5.0)
    assert all(limiter.acquire() for _ in range(5))
    assert not fake.slept


def test_beyond_capacity_waits_for_refill():
    fake, limiter = make(rate=4.0)
    for _ in range(4):
        limiter.acquire()
    assert limiter.acquire() is True
    assert fake.slept == [pytest.approx(0.25)]  # one token at 4 tokens/s
    assert limiter.acquire() is True
    assert fake.slept == [pytest.approx(0.25), pytest.approx(0.25)]


def test_refills_at_the_configured_rate():
    fake, limiter = make(rate=2.0, capacity=10.0)
    for _ in range(10):
        limiter.acquire()
    assert limiter.tokens == pytest.approx(0.0)
    fake.now += 2.0  # 2s * 2 tokens/s = 4 tokens
    assert limiter.tokens == pytest.approx(4.0)
    fake.now += 1.5  # +3 tokens
    assert limiter.tokens == pytest.approx(7.0)
    fake.now += 100.0  # capped at capacity
    assert limiter.tokens == pytest.approx(10.0)
    assert not fake.slept


def test_acquire_returns_false_on_timeout():
    fake, limiter = make(rate=1.0)
    assert limiter.acquire() is True  # burst of 1 consumed
    assert limiter.acquire(timeout=0.5) is False  # next token is 1.0s away
    assert fake.slept == []  # never waited beyond the timeout
    assert limiter.tokens == pytest.approx(0.0)  # a failed acquire consumed nothing
    assert limiter.acquire(timeout=1.0) is True  # the token is exactly 1.0s away
    assert fake.slept == [pytest.approx(1.0)]


def test_rejects_non_positive_rate():
    for rate in (0, -1.0):
        with pytest.raises(ValueError, match="rate must be positive"):
            TokenBucketLimiter(rate)


def test_rejects_capacity_below_one_token():
    with pytest.raises(ValueError, match="capacity must be at least 1"):
        TokenBucketLimiter(2.0, capacity=0)
    with pytest.raises(ValueError, match="capacity must be at least 1"):
        TokenBucketLimiter(2.0, capacity=0.5)


def test_fractional_rate_default_capacity_still_grants_a_token():
    fake, limiter = make(rate=0.5)
    assert limiter.acquire() is True
    assert limiter.acquire() is True
    assert fake.slept == [pytest.approx(2.0)]


async def test_async_limiter_paces_beyond_capacity():
    fake = FakeTime()
    limiter = AsyncTokenBucketLimiter(2.0, clock=fake.clock, sleep=fake.async_sleep)
    assert await limiter.acquire() is True
    assert await limiter.acquire() is True
    assert fake.slept == []
    assert await limiter.acquire() is True
    assert fake.slept == [pytest.approx(0.5)]


async def test_async_acquire_returns_false_on_timeout_without_consuming():
    fake = FakeTime()
    limiter = AsyncTokenBucketLimiter(1.0, clock=fake.clock, sleep=fake.async_sleep)
    assert await limiter.acquire() is True
    assert await limiter.acquire(timeout=0.5) is False
    assert fake.slept == []
    assert limiter.tokens == pytest.approx(0.0)


def test_async_rejects_non_positive_rate():
    with pytest.raises(ValueError, match="rate must be positive"):
        AsyncTokenBucketLimiter(0)


@pytest.mark.parametrize("limiter_class", [TokenBucketLimiter, AsyncTokenBucketLimiter])
@pytest.mark.parametrize("rate", [float("nan"), float("inf")])
def test_rejects_a_non_finite_rate(limiter_class, rate):
    """``nan <= 0`` is false, so an unguarded check accepts it and ``acquire`` then waits ``nan`` seconds forever.

    A hang with no error and no log is the worst possible failure for a limiter sitting in front of ``/user/login``,
    so this must be a ``ValueError`` at construction.
    """
    with pytest.raises(ValueError, match="rate must be positive and finite"):
        limiter_class(rate)


@pytest.mark.parametrize("limiter_class", [TokenBucketLimiter, AsyncTokenBucketLimiter])
@pytest.mark.parametrize("capacity", [float("nan"), float("inf")])
def test_rejects_a_non_finite_capacity(limiter_class, capacity):
    """``nan < 1`` is false too, and an infinite bucket never paces at all."""
    with pytest.raises(ValueError, match="capacity must be at least 1 and finite"):
        limiter_class(2.0, capacity=capacity)


# ---- contention: the lock is not held while sleeping ------------------------------------------------------------
#
# Both limiter docstrings promise that "the lock is never held while sleeping, so one waiting caller does not
# serialise the others". The tests below are the guard for that claim. Each proves it twice over:
#
#   * a *rendezvous*: every waiter must be inside its sleep at the same moment before any of them may leave it.
#     Were the lock held across the sleep, the other waiters would still be blocked on acquiring it, never reach
#     the sleep, and the gate would never open - so a serialising implementation times out here;
#   * a direct check, inside the sleep, that the limiter's lock is free. A non-reentrant lock held by this very
#     caller can never be taken by it, so this fails outright rather than flakily.
#
# Time is faked throughout: the threads and tasks are real, the seconds are not, so nothing waits on the wall
# clock except a failing run hitting its timeout.

WAITERS: int = 8
"""Concurrent waiters. The bucket holds a burst of one, so exactly one is served without waiting."""

GATE_TIMEOUT: float = 5.0
"""How long a waiter gives the others to join it inside the sleep before declaring them serialised."""


class ContendedClock:
    """Fake clock whose ``sleep`` rendezvouses the waiters and then advances time.

    The clock only ever moves inside a sleep, so no token can be refilled until the waiters have all arrived -
    which is what makes the rendezvous deterministic rather than a race won by whoever is scheduled first.
    """

    MIN_TICK: float = 1e-3
    """Floor on a single advance, so a vanishingly small wait cannot leave ``now`` unchanged and spin forever."""

    def __init__(self, expected_sleepers: int) -> None:
        self.now: float = 1000.0
        self.expected: int = expected_sleepers
        self.sleepers: set = set()
        self.violations: List[str] = []
        self.abandoned: bool = False  # once the rendezvous has failed, later waits must not pay for it again
        self.slept: List[float] = []
        self._guard = threading.Lock()

    def clock(self) -> float:
        """Return the fake now."""
        return self.now

    def _advance(self, seconds: float) -> None:
        """Record the requested wait and move the fake clock on."""
        with self._guard:
            self.slept.append(seconds)
            self.now += max(seconds, self.MIN_TICK)

    def _note_sleeper(self, identity: object) -> bool:
        """Record a distinct waiter inside the sleep; ``True`` once all of them are in there together."""
        with self._guard:
            self.sleepers.add(identity)
            return len(self.sleepers) >= self.expected


def test_sync_limiter_does_not_serialise_waiters_behind_one_sleeper():
    """``WAITERS`` real threads, all but one past the burst: every one is served, and none waits on a held lock."""
    fake = ContendedClock(expected_sleepers=WAITERS - 1)
    gate = threading.Event()
    limiter = TokenBucketLimiter(100.0, capacity=1.0, clock=fake.clock, sleep=lambda s: None)

    def sleep(seconds: float) -> None:
        # pylint: disable=protected-access
        if limiter._lock.acquire(timeout=2.0):
            limiter._lock.release()
        else:
            fake.violations.append("the limiter's lock was still held while this caller slept")
        if fake._note_sleeper(threading.get_ident()):
            gate.set()
        if not fake.abandoned and not gate.wait(timeout=GATE_TIMEOUT):
            fake.violations.append("waiters were serialised: they never reached the sleep together")
            fake.abandoned = True
        fake._advance(seconds)

    limiter._sleep = sleep  # pylint: disable=protected-access

    granted: List[bool] = []
    granted_guard = threading.Lock()

    def worker() -> None:
        result = limiter.acquire(timeout=600.0)
        with granted_guard:
            granted.append(result)

    threads = [threading.Thread(target=worker, name=f"waiter-{i}") for i in range(WAITERS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30.0)

    assert not any(thread.is_alive() for thread in threads), "a waiter never finished"
    assert fake.violations == []
    assert granted == [True] * WAITERS, f"only {sum(granted)} of {WAITERS} waiters were served"
    assert len(fake.sleepers) == WAITERS - 1, "the burst serves exactly one caller; every other one must wait"


async def test_async_limiter_does_not_serialise_waiters_behind_one_sleeper():
    """``WAITERS`` concurrent tasks: ``asyncio.gather`` must come back with a grant for every one of them."""
    fake = ContendedClock(expected_sleepers=WAITERS - 1)
    gate = asyncio.Event()
    limiter = AsyncTokenBucketLimiter(100.0, capacity=1.0, clock=fake.clock, sleep=lambda s: None)

    async def sleep(seconds: float) -> None:
        if limiter._lock.locked():  # pylint: disable=protected-access
            # Exact on an event loop: the lock is only ever taken in a block with no await in it, so no other
            # task can be holding it at this suspension point. Locked here means this caller held it.
            fake.violations.append("the limiter's lock was still held while this caller awaited")
        if fake._note_sleeper(id(asyncio.current_task())):
            gate.set()
        await gate.wait()
        fake._advance(seconds)

    limiter._sleep = sleep  # pylint: disable=protected-access

    results = await asyncio.wait_for(
        asyncio.gather(*(limiter.acquire(timeout=600.0) for _ in range(WAITERS))), timeout=GATE_TIMEOUT
    )

    assert fake.violations == []
    assert results == [True] * WAITERS, f"only {sum(results)} of {WAITERS} waiters were served"
    assert len(fake.sleepers) == WAITERS - 1, "the burst serves exactly one caller; every other one must wait"
