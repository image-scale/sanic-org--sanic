"""WebSocket connection."""
from typing import Any, Optional


class WebSocketConnection:
    """WebSocket connection wrapper."""

    def __init__(self, *args, **kwargs):
        pass

    async def send(self, data: Any):
        """Send data."""
        raise NotImplementedError

    async def recv(self) -> Any:
        """Receive data."""
        raise NotImplementedError

    async def close(self, code: int = 1000, reason: str = ""):
        """Close connection."""
        raise NotImplementedError
