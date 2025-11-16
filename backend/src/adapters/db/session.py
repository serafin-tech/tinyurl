"""Database engine and session management (SQLite)."""
import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def _sqlite_url() -> str:
    # Default to a workspace-local path for dev/tests; override via
    # SQLITE_DB_PATH in prod/containers
    path = os.getenv("SQLITE_DB_PATH", os.path.join(
        os.getcwd(), "data", "links.db"))
    # Ensure directory exists for file-based DB in local dev
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return f"sqlite+pysqlite:///{path}"


engine = create_engine(_sqlite_url(), echo=False, future=True)
SessionLocal = sessionmaker(
    bind=engine, class_=Session, expire_on_commit=False, future=True)


def init_db() -> None:
    """Create tables if they don't exist (MVP: no migrations)."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
