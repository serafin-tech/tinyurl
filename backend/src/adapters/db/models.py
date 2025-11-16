"""SQLAlchemy models for TinyURL backend (SQLite)."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class."""


class LinkModel(Base):
    """Link persistence model mapping to links table."""
    __tablename__ = "links"

    link_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    target_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    redirect_code: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    edit_token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def now_utc() -> datetime:
        """Return current UTC datetime."""
        return datetime.now(UTC)
