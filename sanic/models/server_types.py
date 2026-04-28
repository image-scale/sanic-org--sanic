"""Server types."""
from typing import Any, Optional


class ConnInfo:
    """Connection information."""

    __slots__ = (
        "client",
        "client_ip",
        "client_port",
        "server",
        "server_port",
        "ssl",
    )

    def __init__(
        self,
        client: Optional[str] = None,
        client_port: Optional[int] = None,
        server: Optional[str] = None,
        server_port: Optional[int] = None,
        ssl: bool = False,
    ):
        self.client = client
        self.client_ip = client.strip("[]") if client else None
        self.client_port = client_port
        self.server = server
        self.server_port = server_port
        self.ssl = ssl


class Signal:
    """Stub for signal."""

    pass
