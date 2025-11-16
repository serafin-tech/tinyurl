"""Validation helpers for TinyURL domain."""
from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit

from .constants import ALLOWED_REDIRECT_CODES, LINK_ID_PATTERN, MAX_URL_LENGTH, RESERVED_LINK_IDS
from .errors import ValidationError


def normalize_link_id(raw: str) -> str:
    """Lowercase the provided link ID.

    Note: Validation is separate; this only normalizes.
    """
    return raw.lower()


def validate_link_id(link_id: str) -> None:
    """Validate custom link-id against pattern and reserved list."""
    if not LINK_ID_PATTERN.fullmatch(link_id):
        raise ValidationError("link_id must match ^[A-Za-z0-9_-]{1,32}$")
    if link_id in RESERVED_LINK_IDS:
        raise ValidationError("link_id is reserved")


_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*$")


def _punycode_hostname(hostname: str | None) -> str | None:
    if not hostname:
        return hostname
    try:
        return hostname.encode("idna").decode("ascii")
    except Exception as exc:  # pragma: no cover - rare edge
        raise ValidationError("invalid hostname (punycode)") from exc


def normalize_url(raw: str) -> str:
    """Normalize and validate a URL per requirements.

    - Scheme must be http or https
    - Max length 2048
    - Punycode normalization for internationalized domains
    - Disallow private-link schemes like file:, javascript:
    """
    if len(raw) > MAX_URL_LENGTH:
        raise ValidationError("url too long")

    parts = urlsplit(raw)
    scheme = parts.scheme.lower()
    if scheme not in {"http", "https"}:
        raise ValidationError("scheme must be http or https")

    # Basic scheme token validation
    if not _SCHEME_RE.match(scheme):
        raise ValidationError("invalid scheme")

    hostname = _punycode_hostname(parts.hostname)
    # Rebuild netloc preserving userinfo and port
    netloc = ""
    if parts.username:
        netloc += parts.username
        if parts.password:
            netloc += f":{parts.password}"
        netloc += "@"
    if hostname:
        netloc += hostname
    if parts.port:
        netloc += f":{parts.port}"

    normalized = urlunsplit((scheme, netloc, parts.path or "", parts.query, parts.fragment))
    if len(normalized) > MAX_URL_LENGTH:
        raise ValidationError("normalized url too long")
    return normalized


def validate_redirect_code(code: int) -> None:
    """Validate redirect code is within the allowed set."""
    if code not in ALLOWED_REDIRECT_CODES:
        raise ValidationError("redirect_code must be one of 301,302,307,308")
