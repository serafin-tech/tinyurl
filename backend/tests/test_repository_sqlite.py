"""Repository integration tests for SQLite adapter."""

import os

# Ensure SQLite points to a writable path for tests before importing session
_TEST_DB_DIR = os.path.join(os.path.dirname(__file__), ".tmp")
os.environ.setdefault("SQLITE_DB_PATH", os.path.join(_TEST_DB_DIR, "links.db"))

import pytest  # noqa: E402

from src.adapters.db.models import Base  # noqa: E402
from src.adapters.db.repository import LinkRepository  # noqa: E402
from src.adapters.db.session import SessionLocal, engine  # noqa: E402
from src.domain.constants import HTTP_308_PERMANENT_REDIRECT  # noqa: E402
from src.domain.errors import ConflictError, NotFoundError  # noqa: E402


def setup_module() -> None:
    """Ensure tables exist for local SQLite file engine."""
    Base.metadata.create_all(bind=engine)


def test_create_get_update_change_id() -> None:
    """End-to-end repository flow: create, get, update, change_id."""
    with SessionLocal() as session:
        repo = LinkRepository(session)
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


def test_get_not_found() -> None:
    """Fetching missing link should raise NotFoundError (or subclass)."""
    with SessionLocal() as session:
        repo = LinkRepository(session)
        with pytest.raises(NotFoundError):
            repo.get("nope")


def test_create_duplicate_raises_conflict() -> None:
    """Creating a link with an existing link_id should raise ConflictError."""
    with SessionLocal() as session:
        repo = LinkRepository(session)
        # Create the first link
        repo.create(
            link_id="duplicate123",
            target_url="https://example.com",
            redirect_code=301,
            edit_token_hash="h" * 64,
        )
        # Attempt to create another link with the same link_id
        with pytest.raises(ConflictError):
            repo.create(
                link_id="duplicate123",
                target_url="https://another.com",
                redirect_code=302,
                edit_token_hash="g" * 64,
            )


def test_change_id_to_existing_raises_conflict() -> None:
    """Changing link_id to an already-taken ID should raise ConflictError."""
    with SessionLocal() as session:
        repo = LinkRepository(session)
        # Create two links
        repo.create(
            link_id="link1",
            target_url="https://example1.com",
            redirect_code=301,
            edit_token_hash="h" * 64,
        )
        repo.create(
            link_id="link2",
            target_url="https://example2.com",
            redirect_code=301,
            edit_token_hash="g" * 64,
        )
        # Attempt to change link1's ID to link2 (already taken)
        with pytest.raises(ConflictError):
            repo.change_id("link1", "link2")
