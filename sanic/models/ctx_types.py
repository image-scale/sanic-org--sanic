"""Context types."""
from typing import Any, TypeVar


Ctx = TypeVar("Ctx")


class REPLLocal:
    """Local storage for REPL."""

    def __init__(self):
        self.app: Any = None
        self.client: Any = None


__all__ = [
    "Ctx",
    "REPLLocal",
]