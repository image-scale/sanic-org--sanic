"""Socket utilities."""
import os
import socket
from typing import Optional, Tuple


def bind_socket(
    host: str,
    port: int,
    backlog: int = 100,
    reuseaddr: bool = True,
) -> socket.socket:
    """Bind a socket to the given host and port."""
    raise NotImplementedError


def bind_unix_socket(path: str, backlog: int = 100) -> socket.socket:
    """Bind a Unix socket."""
    raise NotImplementedError


def configure_socket(
    host: Optional[str] = None,
    port: Optional[int] = None,
    unix: Optional[str] = None,
    backlog: int = 100,
) -> Tuple[socket.socket, str]:
    """Configure and return a socket."""
    raise NotImplementedError


def remove_unix_socket(path: str) -> None:
    """Remove a Unix socket file."""
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


__all__ = [
    "bind_socket",
    "bind_unix_socket",
    "configure_socket",
    "remove_unix_socket",
]
