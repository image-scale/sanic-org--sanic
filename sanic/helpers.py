"""Sanic helper utilities."""
from typing import Any


class Default:
    """Default value sentinel class."""

    pass


_default = Default()


def import_string(module_name: str) -> Any:
    """Import a module from string."""
    raise NotImplementedError


def is_atty() -> bool:
    """Check if stdout is a TTY."""
    import sys

    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


__all__ = [
    "Default",
    "_default",
    "import_string",
    "is_atty",
]
