"""Domain-level exceptions used across use cases and validators."""
from __future__ import annotations


class DomainError(Exception):
    """Base domain error."""


class ValidationError(DomainError):
    """Input failed validation."""


class ConflictError(DomainError):
    """Resource already exists / conflict (e.g., link_id taken)."""


class NotFoundError(DomainError):
    """Resource not found."""


class GoneError(DomainError):
    """Resource was deleted (410)."""


class UnauthorizedError(DomainError):
    """Missing or invalid edit token."""
