"""Pydantic models for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateLinkRequest(BaseModel):
    """Payload to create a new short link."""
    target_url: str = Field(..., max_length=2048)
    link_id: str | None = Field(None, description="Custom alias (optional)")
    redirect_code: int = Field(301, description="Redirect HTTP status code")


class CreateLinkResponse(BaseModel):
    """Response for a newly created short link including the edit token."""
    link_id: str
    short_url: str
    edit_token: str
    redirect_code: int
    created_at: datetime


class UpdateLinkRequest(BaseModel):
    """Payload to update an existing short link or change its alias."""
    target_url: str | None = None
    redirect_code: int | None = None
    new_link_id: str | None = None


class LinkOut(BaseModel):
    """Canonical link representation returned by read APIs."""
    link_id: str
    target_url: str
    redirect_code: int
    created_at: datetime
    updated_at: datetime
    active: bool
    expires_at: datetime | None
