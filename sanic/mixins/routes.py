"""Routes mixin."""
from functools import partial
from inspect import signature
from typing import Any, Callable, FrozenSet, Optional, Sequence, Union

from sanic.constants import HTTPMethod


class RouteMixin:
    """Route registration mixin."""

    __slots__ = ()

    def route(
        self,
        uri: str,
        methods: Optional[Sequence[str]] = None,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        stream: bool = False,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = False,
        apply: bool = True,
        subprotocols: Optional[Sequence[str]] = None,
        websocket: bool = False,
        unquote: bool = False,
        static: bool = False,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register route decorator."""
        if methods is None:
            methods = frozenset({"GET"})
        else:
            methods = frozenset(m.upper() for m in methods)

        def decorator(handler: Callable) -> Callable:
            # Validate handler signature
            if not websocket:
                sig = signature(handler)
                params = list(sig.parameters.keys())
                if not params or params[0] not in ("request", "req", "r", "_"):
                    # Check if it has at least one parameter
                    if len(params) == 0:
                        raise ValueError(
                            f"Required parameter `request` missing in the {handler.__name__}() route?"
                        )

            self._apply_route(
                handler,
                uri,
                methods,
                host,
                strict_slashes,
                stream,
                version,
                name,
                ignore_body,
                subprotocols,
                websocket,
                static,
                version_prefix,
                error_format,
                ctx_kwargs,
            )
            return handler

        return decorator

    def _apply_route(self, *args, **kwargs):
        """Apply route - to be implemented by subclass."""
        raise NotImplementedError

    def get(
        self,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register GET route."""
        return self.route(
            uri,
            methods=["GET"],
            host=host,
            strict_slashes=strict_slashes,
            version=version,
            name=name,
            ignore_body=ignore_body,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )

    def post(
        self,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        stream: bool = False,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register POST route."""
        return self.route(
            uri,
            methods=["POST"],
            host=host,
            strict_slashes=strict_slashes,
            stream=stream,
            version=version,
            name=name,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )

    def put(
        self,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        stream: bool = False,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register PUT route."""
        return self.route(
            uri,
            methods=["PUT"],
            host=host,
            strict_slashes=strict_slashes,
            stream=stream,
            version=version,
            name=name,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )

    def head(
        self,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register HEAD route."""
        return self.route(
            uri,
            methods=["HEAD"],
            host=host,
            strict_slashes=strict_slashes,
            version=version,
            name=name,
            ignore_body=ignore_body,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )

    def options(
        self,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register OPTIONS route."""
        return self.route(
            uri,
            methods=["OPTIONS"],
            host=host,
            strict_slashes=strict_slashes,
            version=version,
            name=name,
            ignore_body=ignore_body,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )

    def patch(
        self,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        stream: bool = False,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register PATCH route."""
        return self.route(
            uri,
            methods=["PATCH"],
            host=host,
            strict_slashes=strict_slashes,
            stream=stream,
            version=version,
            name=name,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )

    def delete(
        self,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        ignore_body: bool = True,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register DELETE route."""
        return self.route(
            uri,
            methods=["DELETE"],
            host=host,
            strict_slashes=strict_slashes,
            version=version,
            name=name,
            ignore_body=ignore_body,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )

    def websocket(
        self,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        subprotocols: Optional[Sequence[str]] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ) -> Callable:
        """Register websocket route."""
        return self.route(
            uri,
            host=host,
            strict_slashes=strict_slashes,
            subprotocols=subprotocols,
            websocket=True,
            version=version,
            name=name,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )

    def add_route(
        self,
        handler: Callable,
        uri: str,
        methods: Optional[Sequence[str]] = None,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        stream: bool = False,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ):
        """Add route programmatically."""
        route_decorator = self.route(
            uri,
            methods=methods,
            host=host,
            strict_slashes=strict_slashes,
            stream=stream,
            version=version,
            name=name,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )
        return route_decorator(handler)

    def add_websocket_route(
        self,
        handler: Callable,
        uri: str,
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        subprotocols: Optional[Sequence[str]] = None,
        version: Optional[Union[int, str, float]] = None,
        name: Optional[str] = None,
        version_prefix: str = "/v",
        error_format: Optional[str] = None,
        **ctx_kwargs,
    ):
        """Add websocket route programmatically."""
        route_decorator = self.websocket(
            uri,
            host=host,
            strict_slashes=strict_slashes,
            subprotocols=subprotocols,
            version=version,
            name=name,
            version_prefix=version_prefix,
            error_format=error_format,
            **ctx_kwargs,
        )
        return route_decorator(handler)
