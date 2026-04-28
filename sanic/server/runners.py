"""Server runners."""
from typing import Any


def serve(*args, **kwargs) -> None:
    """Serve an app."""
    raise NotImplementedError


def serve_single(*args, **kwargs) -> None:
    """Serve an app in single process."""
    raise NotImplementedError


def serve_multiple(*args, **kwargs) -> None:
    """Serve an app with multiple workers."""
    raise NotImplementedError


def _run_server_forever() -> None:
    """Run server forever."""
    raise NotImplementedError


__all__ = [
    "serve",
    "serve_single",
    "serve_multiple",
    "_run_server_forever",
]
