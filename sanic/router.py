"""Sanic router."""
from typing import Any, Callable, Dict, FrozenSet, Optional, Tuple

from sanic_routing import BaseRouter
from sanic_routing.route import Route


class Router(BaseRouter):
    """Sanic router."""

    DEFAULT_METHOD = "GET"
    ALLOWED_METHODS = frozenset(
        ["GET", "POST", "PUT", "HEAD", "OPTIONS", "PATCH", "DELETE"]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx = type("Context", (), {})()

    def get(self, path: str, method: str, host: Optional[str] = None, **kwargs):
        """Get route for path and method."""
        return self.resolve(
            path=path,
            method=method,
            extra={"host": host} if host else None,
        )

    def add(
        self,
        uri: str,
        methods: FrozenSet[str],
        handler: Callable,
        host: Optional[str] = None,
        strict_slashes: bool = False,
        stream: bool = False,
        ignore_body: bool = False,
        version: Optional[int] = None,
        name: Optional[str] = None,
        unquote: bool = False,
        static: bool = False,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        route_context: Any = None,
        **ctx_kwargs,
    ) -> Route:
        """Add a route."""
        return super().add(
            uri,
            methods=methods,
            handler=handler,
            name=name,
            strict=strict_slashes,
            unquote=unquote,
        )

    @property
    def routes(self):
        """Get all routes."""
        return list(self.static_routes.values()) + list(self.dynamic_routes.values())


__all__ = [
    "Router",
    "Route",
]
