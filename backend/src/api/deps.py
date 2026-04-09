"""FastAPI dependencies for DB collection access and configuration."""

import os
from collections.abc import AsyncIterator

from fastapi import Header, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from src.adapters.db.session import get_db as _get_db


async def get_db() -> AsyncIterator[AsyncIOMotorCollection]:
    """Yield the MongoDB links collection for request lifespan."""
    async for collection in _get_db():
        yield collection


def get_base_url() -> str:
    """Base URL for constructing short URLs (defaults to http://localhost:8000)."""
    return os.getenv("BASE_URL", "http://localhost:8000")


def get_token_pepper() -> str | None:
    """Optional server-side pepper for edit-token hashing."""
    return os.getenv("TOKEN_PEPPER")


def get_permanent_cache_seconds() -> int:
    """Cache max-age (seconds) for permanent redirects (301/308). Default 86400 (1 day)."""
    val = os.getenv("PERMANENT_CACHE_SECONDS", "86400")
    try:
        secs = int(val)
        return max(secs, 0)
    except ValueError:
        return 86400


def get_edit_token(x_edit_token: str | None = Header(default=None)) -> str:
    """Extract edit token from X-Edit-Token header; 401 if missing."""
    if not x_edit_token:
        raise HTTPException(status_code=401, detail="Missing or invalid X-Edit-Token header")
    return x_edit_token
