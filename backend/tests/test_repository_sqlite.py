"""Repository integration tests for SQLite adapter."""

import pytest

from src.adapters.db.repository import LinkRepository
from src.domain.constants import HTTP_308_PERMANENT_REDIRECT
from src.domain.errors import ConflictError, NotFoundError


def test_create_get_update_change_id(db_session) -> None:
    """End-to-end repository flow: create, get, update, change_id."""
    repo = LinkRepository(db_session)
    # Create
    link = repo.create(
        link_id="abc123",
        target_url="https://example.com",
        redirect_code=301,
        edit_token_hash="h" * 64,
    )
    assert link.link_id == "abc123"
    assert repo.exists("abc123")

    # Get
    fetched = repo.get("abc123")
    assert fetched.target_url == "https://example.com"

    # Update
    updated = repo.update(
        "abc123",
        target_url="https://example.com/new",
        redirect_code=HTTP_308_PERMANENT_REDIRECT,
    )
    assert updated.redirect_code == HTTP_308_PERMANENT_REDIRECT
    assert updated.target_url.endswith("/new")

    # Change ID
    changed = repo.change_id("abc123", "def456")
    assert changed.link_id == "def456"
    assert not repo.exists("abc123")
    assert repo.exists("def456")


def test_get_not_found(db_session) -> None:
    """Fetching missing link should raise NotFoundError (or subclass)."""
    repo = LinkRepository(db_session)
    with pytest.raises(NotFoundError):
        repo.get("nope")


def test_create_conflict_and_change_id_conflict(db_session) -> None:
    """Creating duplicate id and changing id to existing should raise ConflictError."""
    repo = LinkRepository(db_session)
    repo.create(
        link_id="dup123",
        target_url="https://example.com/one",
        redirect_code=301,
        edit_token_hash="f" * 64,
    )
    # Commit to persist first create so subsequent rollback doesn't remove it.
    db_session.commit()
    # Duplicate create
    with pytest.raises(ConflictError):
        repo.create(
            link_id="dup123",
            target_url="https://example.com/two",
            redirect_code=302,
            edit_token_hash="e" * 64,
        )
    # Create another and try changing id to existing one
    repo.create(
        link_id="dup456",
        target_url="https://example.com/three",
        redirect_code=301,
        edit_token_hash="d" * 64,
    )
    db_session.commit()
    with pytest.raises(ConflictError):
        repo.change_id("dup456", "dup123")


def test_update_not_found(db_session) -> None:
    """Updating a non-existing id should raise NotFoundError."""
    repo = LinkRepository(db_session)
    with pytest.raises(NotFoundError):
        repo.update("missing", target_url="https://example.com")
