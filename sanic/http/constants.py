"""HTTP constants."""
from enum import IntEnum


class Stage(IntEnum):
    """HTTP processing stage."""

    IDLE = 0
    REQUEST = 1
    HANDLER = 3
    RESPONSE = 4
    FAILED = 5
    CLEANUP = 6


class HTTP(IntEnum):
    """HTTP version."""

    VERSION_1 = 1
    VERSION_1_1 = 11
    VERSION_2 = 2
    VERSION_3 = 3


__all__ = [
    "HTTP",
    "Stage",
]
