import pytest

from src.domain.errors import ValidationError
from src.domain.validators import (
    normalize_link_id,
    normalize_url,
    validate_link_id,
    validate_redirect_code,
)


def test_normalize_and_validate_link_id_ok():
    """Link IDs normalize to lowercase and validate when pattern matches."""
    raw = "My-Link_123"
    normalized = normalize_link_id(raw)
    assert normalized == "my-link_123"
    validate_link_id(normalized)  # should not raise


def test_validate_link_id_invalid_pattern():
    """Invalid characters should raise ValidationError."""
    with pytest.raises(ValidationError):
        validate_link_id("bad space")


def test_validate_link_id_reserved():
    """Reserved IDs should be rejected."""
    with pytest.raises(ValidationError):
        validate_link_id("api")


def test_normalize_url_ok_and_punycode():
    """URLs normalize and apply punycode to internationalized domains."""
    url = "https://exämple.com/path?q=1"
    normalized = normalize_url(url)
    assert normalized.startswith("https://")
    assert "xn--" in normalized  # punycode applied


def test_normalize_url_invalid_scheme():
    """Schemes other than http/https are rejected."""
    with pytest.raises(ValidationError):
        normalize_url("ftp://example.com")


def test_validate_redirect_code():
    """Only allowed redirect codes pass validation."""
    for c in (301, 302, 307, 308):
        validate_redirect_code(c)
    with pytest.raises(ValidationError):
        validate_redirect_code(303)
