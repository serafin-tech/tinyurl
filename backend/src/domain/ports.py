"""Domain repository ports (interfaces) for TinyURL backend.

Inner-layer contracts that adapters must fulfil. Defined as Protocols so
concrete implementations require no explicit inheritance.
"""

from datetime import datetime
from typing import Protocol

from .entities import Link


class LinkRepositoryPort(Protocol):
    """Read/write contract for Link persistence.

    All methods are async to match the async I/O adapter (motor).
    """

    async def get(self, link_id: str) -> Link:
        """Fetch a link by ID or raise NotFoundError."""
        ...

    async def exists(self, link_id: str) -> bool:
        """Return True if a link with the given ID exists."""
        ...

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
        ...

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
        ...

    async def change_id(self, old_id: str, new_id: str) -> Link:
        """Tombstone old alias and create a new one; raise Conflict/NotFound as needed."""
        ...
