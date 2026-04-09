"""Repository integration tests for MongoDB adapter."""

import pytest
from motor.motor_asyncio import AsyncIOMotorCollection

from src.adapters.db.repository import LinkRepository
from src.domain.constants import HTTP_308_PERMANENT_REDIRECT
from src.domain.errors import ConflictError, NotFoundError


@pytest.mark.asyncio
async def test_create_get_update_change_id(
    mongo_collection: AsyncIOMotorCollection,  # type: ignore[type-arg]
) -> None:
    """End-to-end repository flow: create, get, update, change_id."""
    repo = LinkRepository(mongo_collection)

    link = await repo.create(
        link_id="abc123",
        target_url="https://example.com",
        redirect_code=301,
        edit_token_hash="h" * 64,
    )
    assert link.link_id == "abc123"
    assert await repo.exists("abc123")

    fetched = await repo.get("abc123")
    assert fetched.target_url == "https://example.com"

    updated = await repo.update(
        "abc123",
        target_url="https://example.com/new",
        redirect_code=HTTP_308_PERMANENT_REDIRECT,
    )
    assert updated.redirect_code == HTTP_308_PERMANENT_REDIRECT
    assert updated.target_url.endswith("/new")

    changed = await repo.change_id("abc123", "def456")
    assert changed.link_id == "def456"
    assert await repo.exists("abc123")
    old = await repo.get("abc123")
    assert not old.active
    assert await repo.exists("def456")


@pytest.mark.asyncio
async def test_get_not_found(
    mongo_collection: AsyncIOMotorCollection,  # type: ignore[type-arg]
) -> None:
    """Fetching missing link should raise NotFoundError."""
    repo = LinkRepository(mongo_collection)
    with pytest.raises(NotFoundError):
        await repo.get("nope")


@pytest.mark.asyncio
async def test_create_conflict_and_change_id_conflict(
    mongo_collection: AsyncIOMotorCollection,  # type: ignore[type-arg]
) -> None:
    """Creating duplicate id and changing id to existing should raise ConflictError."""
    repo = LinkRepository(mongo_collection)
    await repo.create(
        link_id="dup123",
        target_url="https://example.com/one",
        redirect_code=301,
        edit_token_hash="f" * 64,
    )
    with pytest.raises(ConflictError):
        await repo.create(
            link_id="dup123",
            target_url="https://example.com/two",
            redirect_code=302,
            edit_token_hash="e" * 64,
        )

    await repo.create(
        link_id="dup456",
        target_url="https://example.com/three",
        redirect_code=301,
        edit_token_hash="d" * 64,
    )
    with pytest.raises(ConflictError):
        await repo.change_id("dup456", "dup123")


@pytest.mark.asyncio
async def test_update_not_found(
    mongo_collection: AsyncIOMotorCollection,  # type: ignore[type-arg]
) -> None:
    """Updating a non-existing id should raise NotFoundError."""
    repo = LinkRepository(mongo_collection)
    with pytest.raises(NotFoundError):
        await repo.update("missing", target_url="https://example.com")
