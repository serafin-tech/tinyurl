"""Domain constants and configuration defaults."""
from __future__ import annotations

import re
from typing import Final

# Allowed custom link-id pattern: ^[A-Za-z0-9_-]{1,32}$ per requirements, normalized to lowercase
LINK_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]{1,32}$")

RESERVED_LINK_IDS: Final[set[str]] = {
    "api",
    "admin",
    "robots",
    "favicon",
    "health",
    "metrics",
    "static",
}

# Permitted redirect codes
ALLOWED_REDIRECT_CODES: Final[set[int]] = {301, 302, 307, 308}

# URL constraints
MAX_URL_LENGTH: Final[int] = 2048
