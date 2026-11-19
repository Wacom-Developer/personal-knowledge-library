# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Token-bucket rate limiters for paced PKS logins.

The cache flattens interactive traffic but cannot flatten a sweep (every user is a cold miss) nor a degraded-Redis
fallback to per-pod caching; the limiter is what keeps that work off the ``/user/login`` endpoint. It bounds only
the calls a broker makes with ``paced=True``: interactive calls bypass it, so they are never delayed by it and are
equally never bounded by it.
"""

import asyncio
import math
import threading
import time
from typing import Awaitable, Callable, Optional

from knowledge import logger


def _validate(rate: float, capacity: Optional[float]) -> float:
    """Validate the constructor arguments and return the effective capacity.

    ``capacity`` defaults to ``max(rate, 1)``: a burst of ``rate`` tokens, but never less than one whole token, since a
    bucket that cannot hold one token could never grant an acquire. An explicit ``capacity`` below 1 is rejected for
    the same reason.

    The checks are written as ``not (x > 0)`` rather than ``x <= 0`` so that ``nan`` is rejected: every comparison
    with ``nan`` is false, so ``nan <= 0`` would pass validation and the bucket would then compute a ``nan`` wait
    and sleep forever. ``inf`` is rejected for the same family of reasons - an infinite rate or capacity makes the
    refill arithmetic produce ``nan`` - and a hang is a far worse failure than a ``ValueError``.
    """
    if not (rate > 0) or not math.isfinite(rate):
        raise ValueError("rate must be positive and finite.")
    if capacity is None:
        return max(rate, 1.0)
    if not (capacity >= 1) or not math.isfinite(capacity):
        raise ValueError("capacity must be at least 1 and finite.")
    return float(capacity)


class TokenBucketLimiter:
    """Thread-safe token bucket: bursts up to ``capacity``, then paces at ``rate`` acquires per second.

    The lock guards only the bookkeeping and is never held while sleeping, so one waiting caller does not serialise
    the others; state is re-checked after every wake-up.

    Parameters
    ----------
    rate: float
        Tokens added per second. Must be positive.
    capacity: Optional[float]
        Maximum tokens held, i.e. the burst size. Must be at least 1. Defaults to ``max(rate, 1)``.
    clock: Callable[[], float]
        Monotonic time source in seconds; injectable for tests.
    sleep: Callable[[float], None]
        Blocking sleep; injectable for tests.
    """

    def __init__(
        self,
        rate: float,
        capacity: Optional[float] = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.capacity: float = _validate(rate, capacity)
        self.rate: float = float(rate)
        self._clock = clock
        self._sleep = sleep
        self._lock = threading.Lock()
        self._tokens: float = self.capacity
        self._last_refill: float = clock()

    @property
    def tokens(self) -> float:
        """Tokens currently available, after refilling up to now."""
        with self._lock:
            self._refill()
            return self._tokens

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Take one token, waiting for a refill if needed.

        Parameters
        ----------
        timeout: Optional[float]
            Maximum seconds to wait. ``None`` waits as long as necessary.

        Returns
        -------
        bool
            ``True`` once a token was taken; ``False`` if one would not become available within ``timeout``, in
            which case no token is consumed and the call returns without sleeping.
        """
        deadline = None if timeout is None else self._clock() + timeout
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True
                wait = (1.0 - self._tokens) / self.rate
            if deadline is not None and self._clock() + wait > deadline:
                if logger:
                    logger.debug(f"Token bucket acquire timed out after {timeout}s.")
                return False
            self._sleep(wait)  # lock released: other callers proceed while this one waits

    def _refill(self) -> None:
        """Add tokens for the elapsed time. Caller must hold the lock."""
        now = self._clock()
        elapsed = max(0.0, now - self._last_refill)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_refill = now


class AsyncTokenBucketLimiter:
    """Asyncio token bucket with the same semantics as :class:`TokenBucketLimiter`; never blocks the event loop.

    Parameters
    ----------
    rate: float
        Tokens added per second. Must be positive.
    capacity: Optional[float]
        Maximum tokens held, i.e. the burst size. Must be at least 1. Defaults to ``max(rate, 1)``.
    clock: Callable[[], float]
        Monotonic time source in seconds; injectable for tests.
    sleep: Callable[[float], Awaitable[None]]
        Awaitable sleep; injectable for tests.
    """

    def __init__(
        self,
        rate: float,
        capacity: Optional[float] = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.capacity: float = _validate(rate, capacity)
        self.rate: float = float(rate)
        self._clock = clock
        self._sleep = sleep
        self._lock = asyncio.Lock()
        self._tokens: float = self.capacity
        self._last_refill: float = clock()

    @property
    def tokens(self) -> float:
        """Tokens currently available, after refilling up to now (a point-in-time reading)."""
        self._refill()
        return self._tokens

    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """Take one token, awaiting a refill if needed; ``False`` (nothing consumed) if it would exceed ``timeout``."""
        deadline = None if timeout is None else self._clock() + timeout
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True
                wait = (1.0 - self._tokens) / self.rate
            if deadline is not None and self._clock() + wait > deadline:
                if logger:
                    logger.debug(f"Token bucket acquire timed out after {timeout}s.")
                return False
            await self._sleep(wait)  # lock released: other tasks proceed while this one waits

    def _refill(self) -> None:
        """Add tokens for the elapsed time. Synchronous, so atomic with respect to the event loop."""
        now = self._clock()
        elapsed = max(0.0, now - self._last_refill)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_refill = now
