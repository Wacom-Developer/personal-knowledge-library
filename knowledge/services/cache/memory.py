# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Process-local token store and lock."""

import threading
import time
from typing import Callable, Dict, Optional, Tuple


class InMemoryTokenStore:
    """Bounded, thread-safe, process-local store with per-entry TTL.

    Eviction is oldest-insertion-first once ``max_entries`` is exceeded; an unbounded store at 42k users would hold
    roughly 130MB per pod.

    Parameters
    ----------
    max_entries: int
        Maximum number of entries kept.
    clock: Callable[[], float]
        Monotonic time source in seconds; injectable for tests.
    """

    shared: bool = False

    def __init__(self, max_entries: int = 10_000, clock: Callable[[], float] = time.monotonic) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be at least 1.")
        self.max_entries: int = max_entries
        self._clock = clock
        self._lock = threading.Lock()
        self._data: Dict[str, Tuple[bytes, float]] = {}  # key -> (value, deadline); dict keeps insertion order

    def get(self, key: str) -> Optional[bytes]:
        """Return the value, or ``None`` if absent or expired."""
        with self._lock:
            entry = self._live(key)
            return entry[0] if entry else None

    def set(self, key: str, value: bytes, ttl: float) -> None:
        """Store ``value`` for ``ttl`` seconds, evicting the oldest entries beyond ``max_entries``."""
        with self._lock:
            self._data.pop(key, None)  # re-insert so an overwrite counts as the newest entry
            self._data[key] = (value, self._clock() + ttl)
            while len(self._data) > self.max_entries:
                del self._data[next(iter(self._data))]

    def delete(self, key: str) -> None:
        """Remove ``key`` if present."""
        with self._lock:
            self._data.pop(key, None)

    def ttl(self, key: str) -> Optional[float]:
        """Remaining time-to-live in seconds, or ``None`` if the key is absent or expired."""
        with self._lock:
            entry = self._live(key)
            return entry[1] - self._clock() if entry else None

    def _live(self, key: str) -> Optional[Tuple[bytes, float]]:
        """Return the entry if unexpired, dropping it otherwise. Caller must hold the lock."""
        entry = self._data.get(key)
        if entry is None:
            return None
        if entry[1] <= self._clock():
            del self._data[key]
            return None
        return entry


class InProcessLock:
    """Non-blocking, expiring, thread-safe lock keyed by string; exclusive within one process only.

    Parameters
    ----------
    clock: Callable[[], float]
        Monotonic time source in seconds; injectable for tests.
    """

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._guard = threading.Lock()
        self._held: Dict[str, float] = {}  # key -> deadline

    def acquire(self, key: str, ttl: float) -> bool:
        """Take the lock for at most ``ttl`` seconds; ``False`` if it is held and unexpired."""
        with self._guard:
            now = self._clock()
            deadline = self._held.get(key)
            if deadline is not None and deadline > now:
                return False
            self._held[key] = now + ttl
            return True

    def release(self, key: str) -> None:
        """Release the lock."""
        with self._guard:
            self._held.pop(key, None)
