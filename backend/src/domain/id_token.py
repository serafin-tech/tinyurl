"""Services for link-id generation and edit token management.

Contracts:
- generate_unique_link_id(exists, max_attempts=5) -> str
  - exists(id: str) -> bool is a callable checking persistence for collisions
- generate_edit_token(length=24) -> str (A-Za-z0-9)
- hash_token(token: str, pepper: str | None = None) -> str (hex sha256)
- verify_token(token: str, token_hash: str, pepper: str | None = None) -> bool
"""

import hashlib
import secrets
import string
from collections.abc import Callable

from .errors import GenerationError


def _random_hex_id() -> str:
    # 6 hex chars => 24 bits; requirement: lowercase hex
    return secrets.token_hex(3)


def generate_unique_link_id(exists: Callable[[str], bool], max_attempts: int = 5) -> str:
    """Generate a unique 6-char hex link id with collision retries.

    Args:
        exists: A callable that returns True if the given id already exists.
        max_attempts: Maximum attempts before raising GenerationError.

    Returns:
        str: A unique 6-character lowercase hexadecimal string.

    Raises:
        GenerationError: When a unique id cannot be generated within max_attempts.
    """
    for _ in range(max_attempts):
        candidate = _random_hex_id()
        if not exists(candidate):
            return candidate
    raise GenerationError("failed to generate unique link id")


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
