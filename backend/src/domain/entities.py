"""Domain entities for TinyURL backend."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Link:
    """Represents a shortened link mapping and metadata."""
    link_id: str
    target_url: str
    redirect_code: int
    created_at: datetime
    updated_at: datetime
    edit_token_hash: str
    active: bool = True
    expires_at: datetime | None = None
