"""Pytest fixtures for MongoDB-backed tests using mongomock-motor."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorCollection

from src.api.app import app
from src.api.deps import get_db


@pytest_asyncio.fixture
async def mongo_collection() -> AsyncIterator[AsyncIOMotorCollection]:  # type: ignore[type-arg]
    """Yield an in-process mock MongoDB links collection, cleared between tests."""
    client = AsyncMongoMockClient()
    collection = client["tinyurl"]["links"]
    # Unique index mirrors production setup
    await collection.create_index("link_id", unique=True)
    yield collection
    await collection.drop()


@pytest.fixture(autouse=False)
def override_db(mongo_collection: AsyncIOMotorCollection):  # type: ignore[type-arg]
    """Override the FastAPI get_db dependency to use the test collection."""

    async def _get_test_db() -> AsyncIterator[AsyncIOMotorCollection]:  # type: ignore[type-arg]
        yield mongo_collection

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)
