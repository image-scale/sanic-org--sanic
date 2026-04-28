"""ASGI interface."""
from typing import Any


class ASGIApp:
    """ASGI application wrapper."""

    def __init__(self, sanic_app: Any):
        self.sanic_app = sanic_app

    async def __call__(self, scope: dict, receive, send):
        """Handle ASGI request."""
        raise NotImplementedError


class Lifespan:
    """ASGI Lifespan handler."""

    def __init__(self, app: Any):
        self.app = app

    async def startup(self):
        """Startup."""
        pass

    async def shutdown(self):
        """Shutdown."""
        pass


class MockTransport:
    """Mock transport for ASGI."""

    pass


__all__ = [
    "ASGIApp",
    "Lifespan",
    "MockTransport",
]
