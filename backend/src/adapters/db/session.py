"""MongoDB client and collection access for TinyURL backend."""

import os
from collections.abc import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


def _mongodb_uri() -> str:
    return os.getenv("MONGODB_URI", "mongodb://localhost:27017")


def _db_name() -> str:
    return os.getenv("MONGODB_DB", "tinyurl")


# Module-level client — created once; reused across requests
_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    """Return (or lazily create) the module-level Motor client."""
    global _client  # noqa: PLW0603 - intentional module-level singleton
    if _client is None:
        _client = AsyncIOMotorClient(_mongodb_uri())
    return _client


async def init_db() -> None:
    """Ensure required indexes exist (idempotent)."""
    collection = get_client()[_db_name()]["links"]
    # link_id is the primary identifier; uniqueness enforced at DB level
    await collection.create_index("link_id", unique=True, background=True)


async def get_db() -> AsyncIterator[AsyncIOMotorCollection]:
    """Yield the links collection (no transaction needed for MVP)."""
    yield get_client()[_db_name()]["links"]

