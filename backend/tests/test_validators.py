import pytest

from src.domain.constants import MAX_URL_LENGTH
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


def test_validate_link_id_length_bounds():
    """Link-id length: 1..32 allowed; 33 should fail."""
    validate_link_id("a")
    validate_link_id("a" * 32)
    with pytest.raises(ValidationError):
        validate_link_id("a" * 33)


def test_reserved_after_normalization():
    """Uppercase reserved IDs become reserved after normalization."""
    reserved = normalize_link_id("API")
    with pytest.raises(ValidationError):
        validate_link_id(reserved)


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


def test_normalize_url_uppercase_scheme_ok():
    """Uppercase scheme should normalize and be accepted."""
    out = normalize_url("HTTP://EXAMPLE.com")
    assert out.startswith("http://")


def test_normalize_url_too_long():
    """Reject URLs exceeding MAX_URL_LENGTH prior to normalization."""
    long_path = "a" * (MAX_URL_LENGTH + 1 - len("https://example.com/"))
    with pytest.raises(ValidationError):
        normalize_url(f"https://example.com/{long_path}")


def test_validate_redirect_code():
    """Only allowed redirect codes pass validation."""
    for c in (301, 302, 307, 308):
        validate_redirect_code(c)
    with pytest.raises(ValidationError):
        validate_redirect_code(303)
