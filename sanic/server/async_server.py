"""Async server wrapper."""
from typing import Any, Optional


class AsyncioServer:
    """Asyncio server wrapper."""

    def __init__(
        self,
        app: Any,
        loop: Any,
        serve_coro: Any,
        connections: set,
    ):
        self.app = app
        self.loop = loop
        self.serve_coro = serve_coro
        self.connections = connections
        self._server: Optional[Any] = None
        self._started = False

    def is_serving(self) -> bool:
        """Check if server is serving."""
        if self._server:
            return self._server.is_serving()
        return False

    async def startup(self):
        """Start the server."""
        self._started = True

    async def start_serving(self):
        """Start serving requests."""
        from sanic.exceptions import SanicException

        if not self._started:
            raise SanicException(
                "Cannot run Sanic server without first running await server.startup()"
            )
        if self._server:
            await self._server.start_serving()

    async def serve_forever(self):
        """Serve forever."""
        if self._server:
            await self._server.serve_forever()

    def close(self):
        """Close the server."""
        if self._server:
            self._server.close()

    async def wait_closed(self):
        """Wait for server to close."""
        if self._server:
            await self._server.wait_closed()
