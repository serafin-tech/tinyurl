"""Repository adapter for Link using SQLAlchemy/SQLite."""

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain.entities import Link
from src.domain.errors import ConflictError, NotFoundError

from .models import LinkModel


def _to_entity(model: LinkModel) -> Link:
    return Link(
        link_id=model.link_id,
        target_url=model.target_url,
        redirect_code=model.redirect_code,
        created_at=model.created_at,
        updated_at=model.updated_at,
        edit_token_hash=model.edit_token_hash,
        active=model.active,
        expires_at=model.expires_at,
    )


class LinkRepository:
    """SQLite-backed repository for Link entities."""

    def __init__(self, session: Session):
        self.session = session

    def get(self, link_id: str) -> Link:
        """Fetch a link by ID or raise NotFoundError."""
        model = self.session.get(LinkModel, link_id)
        if not model:
            raise NotFoundError("link not found")
        return _to_entity(model)

    def exists(self, link_id: str) -> bool:
        """Return True if a link with the given ID exists."""
        return self.session.get(LinkModel, link_id) is not None

    def create(  # noqa: PLR0913
        self,
        link_id: str,
        target_url: str,
        redirect_code: int,
        edit_token_hash: str,
        active: bool = True,
        expires_at: datetime | None = None,
    ) -> Link:
        """Create a new link; raise ConflictError if link_id already exists."""
        now = datetime.now(UTC)
        model = LinkModel(
            link_id=link_id,
            target_url=target_url,
            redirect_code=redirect_code,
            created_at=now,
            updated_at=now,
            edit_token_hash=edit_token_hash,
            active=active,
            expires_at=expires_at,
        )
        self.session.add(model)
        try:
            self.session.flush()
        except IntegrityError as exc:  # unique/link_id conflict
            # Ensure session can continue after a failed flush
            self.session.rollback()
            raise ConflictError("link_id already exists") from exc
        return _to_entity(model)

    def update(  # noqa: PLR0913
        self,
        link_id: str,
        *,
        target_url: str | None = None,
        redirect_code: int | None = None,
        active: bool | None = None,
        expires_at: datetime | None = None,
        edit_token_hash: str | None = None,
    ) -> Link:
        """Update mutable fields of a link and return the updated entity."""
        model = self.session.get(LinkModel, link_id)
        if not model:
            raise NotFoundError("link not found")
        if target_url is not None:
            model.target_url = target_url
        if redirect_code is not None:
            model.redirect_code = redirect_code
        if active is not None:
            model.active = active
        if expires_at is not None:
            model.expires_at = expires_at
        if edit_token_hash is not None:
            model.edit_token_hash = edit_token_hash
        model.updated_at = datetime.now(UTC)
        self.session.flush()
        return _to_entity(model)

    def change_id(self, old_id: str, new_id: str) -> Link:
        """Change the primary key by cloning row to new_id and deleting old.

        Tombstoning semantics: we retain the old row but mark it inactive so
        redirects to the old alias return 410 Gone instead of 404 after an
        alias change. We clone data to a new row with the new_id, preserving
        original created_at timestamp and updating updated_at. Old row is
        soft-deactivated.
        """
        old_model = self.session.get(LinkModel, old_id)
        if not old_model:
            raise NotFoundError("link not found")
        if self.session.get(LinkModel, new_id) is not None:
            raise ConflictError("new_link_id already exists")

        # Mark old model inactive (tombstone)
        old_model.active = False
        old_model.updated_at = datetime.now(UTC)

        # Clone into new active model
        new_model = LinkModel(
            link_id=new_id,
            target_url=old_model.target_url,
            redirect_code=old_model.redirect_code,
            created_at=old_model.created_at,
            updated_at=datetime.now(UTC),
            edit_token_hash=old_model.edit_token_hash,
            active=True,
            expires_at=old_model.expires_at,
        )
        self.session.add(new_model)
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("new_link_id already exists") from exc
        return _to_entity(new_model)
