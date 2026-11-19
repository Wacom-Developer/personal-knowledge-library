# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""AES-256-GCM cipher for tokens held in a shared cache.

The associated data is bound to the cache key by the caller, so a ciphertext copied from one user's key to
another's fails to decrypt instead of silently authenticating the wrong user.

Wire format: ``key_id (ascii) + b":" + nonce (12 bytes) + ciphertext_and_tag``.
"""

import os
from typing import Any, Mapping, Optional

_KEY_LENGTH: int = 32
_NONCE_LENGTH: int = 12
_SEPARATOR: bytes = b":"


def _load_aesgcm() -> Any:
    """Import ``AESGCM`` lazily so the base install does not require ``cryptography``."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError(
            "AesGcmCipher requires the 'cryptography' package. Install it with the 'cache' extra: "
            "pip install personal-knowledge-library[cache]"
        ) from exc
    return AESGCM


def _check_key(key_id: str, key: bytes) -> None:
    """Validate a key id and key material, raising ``ValueError`` on bad input."""
    if not key_id or ":" in key_id:
        raise ValueError(f"Invalid key id {key_id!r}: must be non-empty and must not contain ':'.")
    if not key_id.isascii():
        raise ValueError(f"Invalid key id {key_id!r}: must be ASCII.")
    if len(key) != _KEY_LENGTH:
        raise ValueError(f"Key '{key_id}' must be {_KEY_LENGTH} bytes (AES-256), got {len(key)}.")


class AesGcmCipher:
    """AES-256-GCM with key rotation.

    Parameters
    ----------
    key_id: str
        Identifier of the active key, written into every ciphertext. Must not contain ``:``.
    key: bytes
        The active 32-byte key, used for all encryption.
    retired_keys: Optional[Mapping[str, bytes]]
        Former keys by id, still accepted for decryption.
    """

    def __init__(self, key_id: str, key: bytes, retired_keys: Optional[Mapping[str, bytes]] = None) -> None:
        aesgcm = _load_aesgcm()
        keys = {key_id: key, **(retired_keys or {})}
        if retired_keys and key_id in retired_keys:
            raise ValueError(f"Key id '{key_id}' is both active and retired.")
        for kid, material in keys.items():
            _check_key(kid, material)
        self._key_id: bytes = key_id.encode("ascii")
        self._ciphers: dict[bytes, Any] = {kid.encode("ascii"): aesgcm(material) for kid, material in keys.items()}

    def encrypt(self, plaintext: bytes, aad: bytes) -> bytes:
        """Encrypt under the active key with a fresh random nonce."""
        nonce = os.urandom(_NONCE_LENGTH)
        sealed: bytes = self._ciphers[self._key_id].encrypt(nonce, plaintext, aad)
        return self._key_id + _SEPARATOR + nonce + sealed

    def decrypt(self, ciphertext: bytes, aad: bytes) -> bytes:
        """Decrypt with the key named in the ciphertext.

        Raises
        ------
        ValueError
            If the blob is malformed or names an unknown key id.
        cryptography.exceptions.InvalidTag
            If the ciphertext was tampered with or ``aad`` does not match.
        """
        key_id, sep, rest = ciphertext.partition(_SEPARATOR)
        if not sep or len(rest) <= _NONCE_LENGTH:
            raise ValueError("Malformed ciphertext.")
        cipher = self._ciphers.get(key_id)
        if cipher is None:
            raise ValueError("Ciphertext was written with an unknown key id.")
        plaintext: bytes = cipher.decrypt(rest[:_NONCE_LENGTH], rest[_NONCE_LENGTH:], aad)
        return plaintext


class NullCipher:
    """Identity transform. Only for process-local stores; never use with a shared store."""

    def encrypt(self, plaintext: bytes, aad: bytes) -> bytes:  # pylint: disable=unused-argument
        """Return ``plaintext`` unchanged."""
        return plaintext

    def decrypt(self, ciphertext: bytes, aad: bytes) -> bytes:  # pylint: disable=unused-argument
        """Return ``ciphertext`` unchanged."""
        return ciphertext
