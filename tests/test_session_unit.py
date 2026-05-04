# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
"""Unit tests for knowledge/services/session.py.

These tests exercise the pure-Python token-handling logic without contacting
a live PKS stage server: JWTs are minted locally and decoded with
``verify_signature=False`` (the same posture the SDK uses on tokens it
receives from PKS).
"""

import time
from typing import Iterable, Optional

import jwt
import pytest

from knowledge.services.session import (
    PermanentSession,
    RefreshableSession,
    TimedSession,
    TokenManager,
)


def _make_jwt(
    tenant: str = "tenant-a",
    roles: str = "user",
    iss: str = "https://stage.example.com",
    ext_sub: str = "user-1",
    exp: Optional[int] = None,
    omit: Optional[Iterable[str]] = None,
) -> str:
    """Mint a JWT for tests. ``omit`` removes claims to test validation paths."""
    payload = {
        "tenant": tenant,
        "roles": roles,
        "iss": iss,
        "ext-sub": ext_sub,
        "exp": exp if exp is not None else int(time.time()) + 3600,
    }
    if omit:
        for key in omit:
            payload.pop(key, None)
    return jwt.encode(payload, "test-secret", algorithm="HS256")


# ---------------------------------------------------------------------------
# Fix 1: TokenManager must not coerce a missing refresh token to "" — this
# made ``refreshable`` lie and triggered a doomed POST to /refresh on every
# token-handling cycle for PermanentSessions created without an initial
# refresh token.
# ---------------------------------------------------------------------------


def test_add_session_without_refresh_token_creates_non_refreshable_permanent_session() -> None:
    token = _make_jwt(ext_sub="alice")
    manager = TokenManager()

    session = manager.add_session(
        auth_token=token,
        refresh_token=None,
        tenant_api_key="api-key",
        external_user_id="alice",
    )

    assert isinstance(session, PermanentSession)
    assert session.refresh_token is None
    assert session.refreshable is False


def test_add_session_with_refresh_token_keeps_session_refreshable() -> None:
    token = _make_jwt(ext_sub="alice")
    manager = TokenManager()

    session = manager.add_session(
        auth_token=token,
        refresh_token="rt-1",
        tenant_api_key="api-key",
        external_user_id="alice",
    )

    assert isinstance(session, PermanentSession)
    assert session.refresh_token == "rt-1"
    assert session.refreshable is True


# ---------------------------------------------------------------------------
# Fix 2: PermanentSession must reject a constructor ``external_user_id`` that
# does not match the JWT's ``ext-sub`` claim. Previously the two values were
# stored on separate name-mangled attributes and could silently diverge.
# ---------------------------------------------------------------------------


def test_permanent_session_rejects_mismatched_external_user_id() -> None:
    token = _make_jwt(ext_sub="bob")

    with pytest.raises(ValueError, match="ext-sub"):
        PermanentSession(
            tenant_api_key="api-key",
            external_user_id="alice",
            auth_token=token,
            refresh_token="rt-1",
        )


def test_permanent_session_accepts_matching_external_user_id() -> None:
    token = _make_jwt(ext_sub="alice")

    session = PermanentSession(
        tenant_api_key="api-key",
        external_user_id="alice",
        auth_token=token,
        refresh_token="rt-1",
    )

    assert session.external_user_id == "alice"


# ---------------------------------------------------------------------------
# Fix 4: extract_session_id must validate the same five claims as
# _auth_token_details_, raising ValueError instead of leaking KeyError when
# a claim is missing.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("missing_claim", ["tenant", "roles", "exp", "iss", "ext-sub"])
def test_extract_session_id_rejects_jwt_missing_required_claim(missing_claim: str) -> None:
    token = _make_jwt(omit=[missing_claim])

    with pytest.raises(ValueError, match="Invalid authentication token"):
        TimedSession.extract_session_id(token)


def test_extract_session_id_returns_stable_id_for_valid_jwt() -> None:
    token = _make_jwt()

    session_id = TimedSession.extract_session_id(token)

    assert isinstance(session_id, str)
    assert len(session_id) == 64  # sha256 hex


# ---------------------------------------------------------------------------
# Fix 5: update_session must reject empty (and non-string) refresh tokens so a
# valid working refresh token cannot be silently replaced with one that the
# PKS refresh endpoint will reject.
# ---------------------------------------------------------------------------


def _fresh_refreshable_session() -> RefreshableSession:
    token = _make_jwt(ext_sub="alice", tenant="tenant-a", iss="https://stage.example.com")
    return RefreshableSession(auth_token=token, refresh_token="rt-old")


def test_update_session_rejects_empty_refresh_token() -> None:
    session = _fresh_refreshable_session()
    new_auth_token = _make_jwt(ext_sub="alice", tenant="tenant-a", iss="https://stage.example.com")

    with pytest.raises(ValueError, match="non-empty"):
        session.update_session(new_auth_token, "")

    assert session.refresh_token == "rt-old"


def test_update_session_rejects_non_string_refresh_token() -> None:
    session = _fresh_refreshable_session()
    new_auth_token = _make_jwt(ext_sub="alice", tenant="tenant-a", iss="https://stage.example.com")

    with pytest.raises(ValueError, match="non-empty"):
        session.update_session(new_auth_token, None)  # type: ignore[arg-type]

    assert session.refresh_token == "rt-old"


def test_update_session_accepts_valid_refresh_token() -> None:
    session = _fresh_refreshable_session()
    new_auth_token = _make_jwt(ext_sub="alice", tenant="tenant-a", iss="https://stage.example.com")

    session.update_session(new_auth_token, "rt-new")

    assert session.refresh_token == "rt-new"
    assert session.auth_token == new_auth_token


def test_update_session_rejects_token_for_different_user() -> None:
    session = _fresh_refreshable_session()
    foreign_token = _make_jwt(ext_sub="bob", tenant="tenant-a", iss="https://stage.example.com")

    with pytest.raises(ValueError, match="different user"):
        session.update_session(foreign_token, "rt-new")
