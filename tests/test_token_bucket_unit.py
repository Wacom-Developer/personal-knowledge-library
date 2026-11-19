# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the token-bucket limiters; deterministic, never sleeps on the wall clock."""

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
