"""HTTP protocol."""
import asyncio

from typing import Any, Optional

from sanic.server.protocols.base_protocol import SanicProtocol


class HttpProtocol(SanicProtocol):
    """HTTP protocol handler."""

    def __init__(
        self,
        *,
        app: Any = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        signal: Any = None,
        connections: Optional[set] = None,
        state: Any = None,
        unix: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(app=app, loop=loop, **kwargs)
        self.signal = signal
        self.connections = connections or set()
        self.state = state
        self.unix = unix

    def connection_made(self, transport: asyncio.Transport):
        """Handle connection made."""
        super().connection_made(transport)
        self.connections.add(self)

    def connection_lost(self, exc: Optional[Exception]):
        """Handle connection lost."""
        super().connection_lost(exc)
        self.connections.discard(self)

    def data_received(self, data: bytes):
        """Handle data received."""
        pass
