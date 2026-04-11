"""Services for generated link-id candidates and edit token management."""

import hashlib
import secrets
import string

LINK_ID_GENERATION_MAX_ATTEMPTS = 5


def generate_link_id_candidate() -> str:
    """Return a random 6-character lowercase hexadecimal candidate ID."""
    return secrets.token_hex(3)


_ALPHANUM = string.ascii_letters + string.digits


def generate_edit_token(length: int = 24) -> str:
    """Generate a high-entropy token consisting of [A-Za-z0-9].

    Args:
        length: The length of the token to generate. Defaults to 24.

    Returns:
        str: Random string using only ASCII letters and digits (A-Za-z0-9).
    """
    return "".join(secrets.choice(_ALPHANUM) for _ in range(length))


def _compute_hash(token: str, pepper: str | None) -> str:
    h = hashlib.sha256()
    if pepper:
        h.update(pepper.encode("utf-8"))
    h.update(token.encode("utf-8"))
    return h.hexdigest()


def hash_token(token: str, pepper: str | None = None) -> str:
    """Compute a SHA-256 hash of the token (optionally prepended with pepper).

    Args:
        token (str): The token to hash.
        pepper (str | None, optional): Optional secret value to prepend before hashing.

    Returns:
        str: A 64-character lowercase hexadecimal string representing the SHA-256 hash.
    """
    return _compute_hash(token, pepper)


def verify_token(token: str, token_hash: str, pepper: str | None = None) -> bool:
    """Verify that a token matches a stored hash using constant-time comparison.

    Args:
        token (str): The plaintext token to verify.
        token_hash (str): The expected hex-encoded SHA-256 hash to compare against.
        pepper (str | None): Optional secret value to prepend to the token before hashing.

    Returns:
        bool: True if the token matches the hash, False otherwise.

    Security:
        Uses constant-time comparison to prevent timing attacks.
    """
    expected = _compute_hash(token, pepper)
    return secrets.compare_digest(expected, token_hash)
