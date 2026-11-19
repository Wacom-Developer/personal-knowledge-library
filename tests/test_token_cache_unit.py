# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Unit tests for the token cache foundation: cipher, in-memory store and in-process lock. No network."""

import pytest

from knowledge.services.cache.crypto import AesGcmCipher, NullCipher
from knowledge.services.cache.memory import InMemoryTokenStore, InProcessLock

KEY_1 = bytes(range(32))
KEY_2 = bytes(range(32, 64))


class FakeClock:
    """Manually advanced clock."""

    def __init__(self) -> None:
        self.now: float = 1000.0

    def __call__(self) -> float:
        return self.now


def test_round_trip_returns_plaintext():
    cipher = AesGcmCipher("v1", KEY_1)
    blob = cipher.encrypt(b"secret-token", b"tok:user-a")
    assert cipher.decrypt(blob, b"tok:user-a") == b"secret-token"


def test_ciphertext_differs_across_calls():
    cipher = AesGcmCipher("v1", KEY_1)
    assert cipher.encrypt(b"same", b"aad") != cipher.encrypt(b"same", b"aad")


def test_aad_mismatch_rejects():
    cipher = AesGcmCipher("v1", KEY_1)
    blob = cipher.encrypt(b"secret-token", b"tok:a")
    with pytest.raises(Exception):
        cipher.decrypt(blob, b"tok:b")


def test_decrypts_with_retired_key():
    old = AesGcmCipher("v1", KEY_1)
    blob = old.encrypt(b"payload", b"aad")
    rotated = AesGcmCipher("v2", KEY_2, retired_keys={"v1": KEY_1})
    assert rotated.decrypt(blob, b"aad") == b"payload"
    # new writes use the active key and are not readable by the old cipher
    new_blob = rotated.encrypt(b"x", b"aad")
    assert new_blob.startswith(b"v2:")
    with pytest.raises(Exception):
        old.decrypt(new_blob, b"aad")


def test_unknown_key_id_rejects():
    blob = AesGcmCipher("v1", KEY_1).encrypt(b"payload", b"aad")
    with pytest.raises(Exception):
        AesGcmCipher("v2", KEY_2).decrypt(blob, b"aad")


def test_rejects_key_of_wrong_length():
    with pytest.raises(ValueError):
        AesGcmCipher("v1", bytes(16))
    with pytest.raises(ValueError):
        AesGcmCipher("v2", KEY_2, retired_keys={"v1": bytes(16)})


def test_rejects_key_id_containing_colon():
    with pytest.raises(ValueError):
        AesGcmCipher("v:1", KEY_1)
    with pytest.raises(ValueError):
        AesGcmCipher("v2", KEY_2, retired_keys={"v:1": KEY_1})


def test_null_cipher_is_identity():
    cipher = NullCipher()
    assert cipher.encrypt(b"abc", b"aad") == b"abc"
    assert cipher.decrypt(b"abc", b"aad") == b"abc"


def test_store_returns_none_after_ttl_elapses():
    clock = FakeClock()
    store = InMemoryTokenStore(clock=clock)
    store.set("k", b"v", ttl=10)
    assert store.get("k") == b"v"
    assert store.ttl("k") == pytest.approx(10)
    clock.now += 4
    assert store.ttl("k") == pytest.approx(6)
    clock.now += 6
    assert store.get("k") is None
    assert store.ttl("k") is None


def test_store_ttl_is_none_for_absent_key():
    assert InMemoryTokenStore().ttl("missing") is None


def test_store_delete_removes_entry():
    store = InMemoryTokenStore()
    store.set("k", b"v", ttl=10)
    store.delete("k")
    store.delete("k")  # idempotent
    assert store.get("k") is None


def test_store_evicts_oldest_beyond_max_entries():
    store = InMemoryTokenStore(max_entries=2)
    store.set("a", b"1", ttl=100)
    store.set("b", b"2", ttl=100)
    store.set("c", b"3", ttl=100)
    assert store.get("a") is None
    assert store.get("b") == b"2"
    assert store.get("c") == b"3"


def test_store_overwrite_does_not_evict_and_refreshes_age():
    store = InMemoryTokenStore(max_entries=2)
    store.set("a", b"1", ttl=100)
    store.set("b", b"2", ttl=100)
    store.set("a", b"1b", ttl=100)  # overwrite: a becomes newest
    store.set("c", b"3", ttl=100)  # evicts b, the oldest insertion
    assert store.get("a") == b"1b"
    assert store.get("b") is None
    assert store.get("c") == b"3"


def test_in_memory_store_is_not_shared():
    assert InMemoryTokenStore().shared is False
    assert InMemoryTokenStore().max_entries == 10_000


def test_lock_is_exclusive_until_released():
    lock = InProcessLock()
    assert lock.acquire("k", ttl=30) is True
    assert lock.acquire("k", ttl=30) is False
    assert lock.acquire("other", ttl=30) is True
    lock.release("k")
    assert lock.acquire("k", ttl=30) is True


def test_lock_is_reacquirable_after_ttl():
    clock = FakeClock()
    lock = InProcessLock(clock=clock)
    assert lock.acquire("k", ttl=5) is True
    clock.now += 4
    assert lock.acquire("k", ttl=5) is False
    clock.now += 1
    assert lock.acquire("k", ttl=5) is True
