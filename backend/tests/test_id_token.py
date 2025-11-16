"""Unit tests for ID and token services."""

import itertools

import pytest

from src.domain import id_token as mod
from src.domain.errors import GenerationError
from src.domain.id_token import (
    generate_edit_token,
    generate_unique_link_id,
    hash_token,
    verify_token,
)


def test_generate_unique_link_id_no_collision() -> None:
    """Simple path: generates a 6-char lowercase hex id with no collision."""
    ids: set[str] = set()
    exists = ids.__contains__
    new_id = generate_unique_link_id(exists)
    assert isinstance(new_id, str) and len(new_id) == 6
    assert all(ch in "0123456789abcdef" for ch in new_id)


def test_generate_unique_link_id_with_collision_then_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """First candidate collides, second is unique."""
    seq = itertools.cycle(["deadbe", "b16b00"])

    def fake_token_hex(n: int) -> str:  # noqa: ARG001 - test helper signature
        return next(seq)[: 2 * n]

    monkeypatch.setattr(mod.secrets, "token_hex", fake_token_hex)

    taken = {"deadbe"}
    new_id = mod.generate_unique_link_id(taken.__contains__)
    assert new_id == "b16b00"


def test_generate_unique_link_id_exhaustion(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exhaust retries and raise GenerationError on repeated collisions."""

    def always_collision(*_args: object, **_kwargs: object) -> str:
        return "ffffff"

    monkeypatch.setattr(mod.secrets, "token_hex", always_collision)
    with pytest.raises(GenerationError):
        mod.generate_unique_link_id(lambda _: True, max_attempts=3)


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
