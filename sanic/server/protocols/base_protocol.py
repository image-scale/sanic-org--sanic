"""Base protocol."""
import asyncio

from typing import Any, Optional


class SanicProtocol(asyncio.Protocol):
    """Base Sanic protocol."""

    def __init__(
        self,
        *,
        app: Any = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        **kwargs,
    ):
        self.app = app
        self.loop = loop or asyncio.get_event_loop()
        self.transport: Optional[asyncio.Transport] = None
        self.connections: set = set()

    def connection_made(self, transport: asyncio.Transport):
        """Handle connection made."""
        self.transport = transport

    def connection_lost(self, exc: Optional[Exception]):
        """Handle connection lost."""
        pass

    def data_received(self, data: bytes):
        """Handle data received."""
        pass
