"""Sanic constants."""
from enum import auto, Enum
from typing import FrozenSet


class StrEnum(str, Enum):
    """String Enum base class."""

    def _generate_next_value_(name, *args):
        return name.upper()

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self) -> int:
        return hash(self.value)

    def lower(self) -> str:
        return self.value.lower()

    def upper(self) -> str:
        return self.value.upper()


class HTTPMethod(StrEnum):
    """HTTP Methods."""

    GET = auto()
    POST = auto()
    PUT = auto()
    HEAD = auto()
    OPTIONS = auto()
    PATCH = auto()
    DELETE = auto()


HTTP_METHODS: FrozenSet[HTTPMethod] = frozenset(HTTPMethod)

DEFAULT_HTTP_CONTENT_TYPE = "application/octet-stream"

IDEMPOTENT_METHODS = frozenset(("GET", "HEAD", "PUT", "DELETE", "OPTIONS"))
SAFE_METHODS = frozenset(("GET", "HEAD", "OPTIONS"))
CACHEABLE_METHODS = frozenset(("GET", "HEAD"))


class LocalCertCreator(StrEnum):
    """Local certificate creator types."""

    AUTO = auto()
    MKCERT = auto()
    TRUSTME = auto()


class RestartOrder(StrEnum):
    """Restart order options."""

    SHUTDOWN_FIRST = auto()
    STARTUP_FIRST = auto()


# Re-exports
__all__ = [
    "HTTPMethod",
    "HTTP_METHODS",
    "DEFAULT_HTTP_CONTENT_TYPE",
    "IDEMPOTENT_METHODS",
    "SAFE_METHODS",
    "CACHEABLE_METHODS",
    "LocalCertCreator",
    "RestartOrder",
]
