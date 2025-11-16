"""Pytest fixtures and environment setup for tests."""

import os
from collections.abc import Iterator

import pytest

from src.adapters.db.models import Base
from src.adapters.db.session import SessionLocal, engine


# Ensure SQLite points to a writable path for tests before session usage
_TEST_DB_DIR = os.path.join(os.path.dirname(__file__), ".tmp")
os.makedirs(_TEST_DB_DIR, exist_ok=True)
os.environ.setdefault("SQLITE_DB_PATH", os.path.join(_TEST_DB_DIR, "links.db"))


@pytest.fixture(scope="session", autouse=True)
def init_db() -> None:
    """Create tables once per test session."""
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session() -> Iterator[SessionLocal]:
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
