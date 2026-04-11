"""Unit tests for ID and token services."""

import pytest

from src.domain import id_token as mod
from src.domain.id_token import (
    LINK_ID_GENERATION_MAX_ATTEMPTS,
    generate_edit_token,
    generate_link_id_candidate,
    hash_token,
    verify_token,
)


def test_generate_link_id_candidate_format() -> None:
    """Generated candidates use the required 6-char lowercase hexadecimal format."""
    new_id = generate_link_id_candidate()
    assert isinstance(new_id, str) and len(new_id) == 6
    assert all(ch in "0123456789abcdef" for ch in new_id)


def test_generate_link_id_candidate_uses_three_random_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Candidate generation should request exactly 3 random bytes (6 hex chars)."""

    def fake_token_hex(n: int) -> str:
        assert n == 3
        return "abcdef"

    monkeypatch.setattr(mod.secrets, "token_hex", fake_token_hex)
    assert generate_link_id_candidate() == "abcdef"


def test_link_id_generation_retry_budget_matches_requirement() -> None:
    """Auto-generated IDs should retry collisions up to five times."""
    assert LINK_ID_GENERATION_MAX_ATTEMPTS == 5


def test_edit_token_hash_and_verify() -> None:
    """Verify hash/compare works without pepper."""
    token = generate_edit_token()
    assert len(token) == 24
    h = hash_token(token)
    assert isinstance(h, str) and len(h) == 64
    assert verify_token(token, h)
    assert not verify_token(token + "x", h)


def test_edit_token_hash_and_verify_with_pepper() -> None:
    """Verify hash/compare works with pepper and fails on different pepper."""
    token = generate_edit_token()
    pepper = "server-side-pepper"
    h = hash_token(token, pepper=pepper)
    assert verify_token(token, h, pepper=pepper)
    assert not verify_token(token, h, pepper=pepper + "x")
