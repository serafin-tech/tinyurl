"""Repository adapter for Link using Motor (async MongoDB)."""

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from src.domain.entities import Link
from src.domain.errors import ConflictError, NotFoundError


def _doc_to_entity(doc: dict[str, object]) -> Link:
    return Link(
        link_id=str(doc["link_id"]),
        target_url=str(doc["target_url"]),
        redirect_code=int(doc["redirect_code"]),  # type: ignore[call-overload]
        created_at=doc["created_at"],  # type: ignore[arg-type]
        updated_at=doc["updated_at"],  # type: ignore[arg-type]
        edit_token_hash=str(doc["edit_token_hash"]),
        active=bool(doc.get("active", True)),
        expires_at=doc.get("expires_at"),  # type: ignore[arg-type]
    )


class LinkRepository:
    """MongoDB-backed async repository for Link entities."""

    def __init__(self, collection: AsyncIOMotorCollection):
        self._col = collection

    async def get(self, link_id: str) -> Link:
        """Fetch a link by ID or raise NotFoundError."""
        doc = await self._col.find_one({"link_id": link_id})
        if doc is None:
            raise NotFoundError("link not found")
        return _doc_to_entity(doc)

    async def exists(self, link_id: str) -> bool:
        """Return True if a link with the given ID exists."""
        doc = await self._col.find_one({"link_id": link_id}, {"_id": 1})
        return doc is not None

    async def create(  # noqa: PLR0913
        self,
        link_id: str,
        target_url: str,
        redirect_code: int,
        edit_token_hash: str,
        active: bool = True,
        expires_at: datetime | None = None,
    ) -> Link:
        """Persist a new link; raise ConflictError if link_id already exists."""
        now = datetime.now(UTC)
        doc = {
            "link_id": link_id,
            "target_url": target_url,
            "redirect_code": redirect_code,
            "created_at": now,
            "updated_at": now,
            "edit_token_hash": edit_token_hash,
            "active": active,
            "expires_at": expires_at,
        }
        try:
            await self._col.insert_one(doc)
        except DuplicateKeyError as exc:
            raise ConflictError("link_id already exists") from exc
        return _doc_to_entity(doc)

    async def update(  # noqa: PLR0913
        self,
        link_id: str,
        *,
        target_url: str | None = None,
        redirect_code: int | None = None,
        active: bool | None = None,
        expires_at: datetime | None = None,
        edit_token_hash: str | None = None,
    ) -> Link:
        """Update mutable fields; raise NotFoundError if link not found."""
        changes: dict[str, object] = {"updated_at": datetime.now(UTC)}
        if target_url is not None:
            changes["target_url"] = target_url
        if redirect_code is not None:
            changes["redirect_code"] = redirect_code
        if active is not None:
            changes["active"] = active
        if expires_at is not None:
            changes["expires_at"] = expires_at
        if edit_token_hash is not None:
            changes["edit_token_hash"] = edit_token_hash

        doc = await self._col.find_one_and_update(
            {"link_id": link_id},
            {"$set": changes},
            return_document=ReturnDocument.AFTER,
        )
        if doc is None:
            raise NotFoundError("link not found")
        return _doc_to_entity(doc)

    async def change_id(self, old_id: str, new_id: str) -> Link:
        """Tombstone old alias and clone to new alias.

        Tombstoning semantics: old alias becomes inactive (410 Gone) while
        new alias takes over. Original created_at is preserved.
        """
        old_doc = await self._col.find_one({"link_id": old_id})
        if old_doc is None:
            raise NotFoundError("link not found")

        now = datetime.now(UTC)
        new_doc = {
            "link_id": new_id,
            "target_url": old_doc["target_url"],
            "redirect_code": old_doc["redirect_code"],
            "created_at": old_doc["created_at"],
            "updated_at": now,
            "edit_token_hash": old_doc["edit_token_hash"],
            "active": True,
            "expires_at": old_doc.get("expires_at"),
        }
        try:
            await self._col.insert_one(new_doc)
        except DuplicateKeyError as exc:
            raise ConflictError("new_link_id already exists") from exc

        # Tombstone old alias after successful insert
        await self._col.update_one(
            {"link_id": old_id},
            {"$set": {"active": False, "updated_at": now}},
        )
        return _doc_to_entity(new_doc)

