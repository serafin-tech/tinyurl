"""FastAPI dependencies for DB sessions and configuration."""

import os
from collections.abc import Iterator

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from src.adapters.db.session import SessionLocal


def get_db() -> Iterator[Session]:
    """Yield a SQLAlchemy Session for request lifespan with commit/rollback.

    Commits the transaction if the request handling succeeds, otherwise rolls back.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_base_url() -> str:
    """Base URL for constructing short URLs (defaults to http://localhost:8000)."""
    return os.getenv("BASE_URL", "http://localhost:8000")


def get_token_pepper() -> str | None:
    """Optional server-side pepper for edit-token hashing."""
    return os.getenv("EDIT_TOKEN_PEPPER")


def get_edit_token(x_edit_token: str | None = Header(default=None)) -> str:
    """Extract edit token from X-Edit-Token header; 401 if missing."""
    if not x_edit_token:
        raise HTTPException(status_code=401, detail="missing edit token")
    return x_edit_token
