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
from src.domain.errors import NotFoundError  # noqa: E402


def setup_module() -> None:
    """Ensure tables exist for local SQLite file engine."""
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a clean database session for each test with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        # Clean up: delete all test data
        session.rollback()
        session.execute(Base.metadata.tables["links"].delete())
        session.commit()
        session.close()


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
