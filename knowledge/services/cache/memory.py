# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Process-local token store and lock, plus the awaitable adapters the async broker defaults to."""

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


class AsyncInMemoryTokenStore:
    """Awaitable adapter over a process-local :class:`InMemoryTokenStore`.

    The async broker is typed against ``AsyncTokenStore``, and the in-memory store is the default it falls back to
    when no shared backend is configured. Its operations are a dictionary lookup under a short-lived mutex - no
    I/O, nothing that can wait - so presenting them as coroutines costs an await and never yields to the loop or
    stalls it. There is deliberately no second storage implementation here: this delegates to the one above.

    The adapted type is :class:`InMemoryTokenStore` rather than the ``TokenStore`` protocol at large, because an
    adapter accepting any synchronous store would invite wrapping a blocking network backend, which is exactly
    what an event loop must not do. A shared backend needs a natively asynchronous client instead.

    Parameters
    ----------
    store: Optional[InMemoryTokenStore]
        Store to adapt, for callers that need to size or clock it. Defaults to a fresh one.
    """

    def __init__(self, store: Optional["InMemoryTokenStore"] = None) -> None:
        self._store: InMemoryTokenStore = store if store is not None else InMemoryTokenStore()

    @property
    def shared(self) -> bool:
        """``True`` when other processes can read the adapted store."""
        return self._store.shared

    async def get(self, key: str) -> Optional[bytes]:
        """Return the value, or ``None`` if absent or expired."""
        return self._store.get(key)

    async def set(self, key: str, value: bytes, ttl: float) -> None:
        """Store ``value`` for ``ttl`` seconds."""
        self._store.set(key, value, ttl)

    async def delete(self, key: str) -> None:
        """Remove ``key`` if present."""
        self._store.delete(key)

    async def ttl(self, key: str) -> Optional[float]:
        """Remaining time-to-live in seconds, or ``None`` if the key is absent or expired."""
        return self._store.ttl(key)


class AsyncInProcessLock:
    """Awaitable adapter over :class:`InProcessLock`; exclusive within one process only.

    Like the store above, the adapted operations are pure in-memory bookkeeping, so they are never a reason to
    yield. See :class:`AsyncInMemoryTokenStore` for why this adapts the concrete lock rather than the protocol.

    Parameters
    ----------
    lock: Optional[InProcessLock]
        Lock to adapt, for callers that need to clock it. Defaults to a fresh one.
    """

    def __init__(self, lock: Optional["InProcessLock"] = None) -> None:
        self._lock: InProcessLock = lock if lock is not None else InProcessLock()

    async def acquire(self, key: str, ttl: float) -> bool:
        """Take the lock for at most ``ttl`` seconds; ``False`` if it is held and unexpired."""
        return self._lock.acquire(key, ttl)

    async def release(self, key: str) -> None:
        """Release the lock."""
        self._lock.release(key)
