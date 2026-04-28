"""WebSocket protocol."""
import asyncio

from typing import Any, Optional


class WebSocketProtocol(asyncio.Protocol):
    """WebSocket protocol handler."""

    def __init__(
        self,
        *,
        app: Any = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        websocket_max_size: int = 2**20,
        websocket_ping_interval: int = 20,
        websocket_ping_timeout: int = 20,
        **kwargs,
    ):
        self.app = app
        self.loop = loop
        self.websocket_max_size = websocket_max_size
        self.websocket_ping_interval = websocket_ping_interval
        self.websocket_ping_timeout = websocket_ping_timeout
