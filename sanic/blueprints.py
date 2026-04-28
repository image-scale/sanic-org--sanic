"""Sanic blueprints."""
from __future__ import annotations

import re

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Union,
)

from sanic.base.root import BaseSanic
from sanic.exceptions import SanicException
from sanic.mixins.exceptions import ExceptionMixin
from sanic.mixins.listeners import ListenerMixin
from sanic.mixins.middleware import MiddlewareMixin
from sanic.mixins.routes import RouteMixin
from sanic.mixins.signals import SignalMixin
from sanic.mixins.static import StaticMixin
from sanic.models.futures import (
    FutureException,
    FutureListener,
    FutureMiddleware,
    FutureRoute,
    FutureSignal,
    FutureStatic,
)


if TYPE_CHECKING:
    from sanic.app import Sanic


class Blueprint(
    BaseSanic,
    RouteMixin,
    MiddlewareMixin,
    ListenerMixin,
    ExceptionMixin,
    SignalMixin,
    StaticMixin,
):
    """Blueprint for grouping routes and handlers."""

    __slots__ = (
        "_apps",
        "_future_routes",
        "_future_middleware",
        "_future_listeners",
        "_future_exceptions",
        "_future_signals",
        "_future_statics",
        "url_prefix",
        "host",
        "version",
        "version_prefix",
        "strict_slashes",
    )

    def __init__(
        self,
        name: str,
        url_prefix: Optional[str] = None,
        host: Optional[str] = None,
        version: Optional[Union[int, str, float]] = None,
        strict_slashes: Optional[bool] = None,
        version_prefix: str = "/v",
    ):
        super().__init__(name)

        self._apps: Set[Sanic] = set()
        self._future_routes: List[FutureRoute] = []
        self._future_middleware: List[FutureMiddleware] = []
        self._future_listeners: List[FutureListener] = []
        self._future_exceptions: List[FutureException] = []
        self._future_signals: List[FutureSignal] = []
        self._future_statics: List[FutureStatic] = []

        self.url_prefix = url_prefix
        self.host = host
        self.version = version
        self.version_prefix = version_prefix
        self.strict_slashes = strict_slashes

    def __str__(self) -> str:
        return f"<Blueprint {self.name}>"

    def __repr__(self) -> str:
        return (
            f'Blueprint(name="{self.name}", url_prefix={self.url_prefix!r}, '
            f"host={self.host!r}, version={self.version!r}, "
            f"strict_slashes={self.strict_slashes!r})"
        )

    @property
    def apps(self) -> Set["Sanic"]:
        """Get registered apps."""
        if not self._apps:
            raise SanicException(
                f"{self} has not yet been registered to an app"
            )
        return self._apps

    def _apply_route(
        self,
        handler: Callable,
        uri: str,
        methods: FrozenSet[str],
        host: Optional[str],
        strict_slashes: Optional[bool],
        stream: bool,
        version: Optional[Union[int, str, float]],
        name: Optional[str],
        ignore_body: bool,
        subprotocols: Optional[Sequence[str]],
        websocket: bool,
        static: bool,
        version_prefix: str,
        error_format: Optional[str],
        ctx_kwargs: dict,
    ):
        """Apply route to blueprint."""
        route = FutureRoute(
            handler=handler,
            uri=uri,
            methods=methods,
            host=host,
            strict_slashes=strict_slashes,
            stream=stream,
            version=version,
            name=name,
            ignore_body=ignore_body,
            version_prefix=version_prefix,
            error_format=error_format,
            static=static,
            ctx_kwargs=ctx_kwargs,
        )
        self._future_routes.append(route)

    def _apply_middleware(self, middleware: Callable, attach_to: str, priority: int):
        """Apply middleware to blueprint."""
        self._future_middleware.append(
            FutureMiddleware(middleware, attach_to, priority)
        )

    def _apply_listener(self, event: str, listener: Callable):
        """Apply listener to blueprint."""
        self._future_listeners.append(FutureListener(listener, event))

    def _apply_exception_handler(self, exceptions, handler: Callable):
        """Apply exception handler to blueprint."""
        if isinstance(exceptions[0], (list, tuple)):
            exceptions = exceptions[0]
        self._future_exceptions.append(FutureException(handler, exceptions))

    def _apply_signal(self, handler: Callable, event: str, condition: Optional[dict]):
        """Apply signal to blueprint."""
        self._future_signals.append(FutureSignal(handler, event, condition))

    def register(self, app: "Sanic", options: Optional[Dict[str, Any]] = None):
        """Register blueprint with app."""
        self._apps.add(app)
        # Registration logic handled by app.blueprint()

    def copy(
        self,
        name: str,
        url_prefix: Optional[str] = None,
        version: Optional[Union[int, str, float]] = None,
        version_prefix: str = "/v",
        strict_slashes: Optional[bool] = None,
        with_registration: bool = True,
        with_ctx: bool = False,
    ) -> "Blueprint":
        """Create a copy of the blueprint."""
        new_bp = Blueprint(
            name=name,
            url_prefix=url_prefix if url_prefix is not None else self.url_prefix,
            version=version if version is not None else self.version,
            version_prefix=version_prefix,
            strict_slashes=strict_slashes if strict_slashes is not None else self.strict_slashes,
        )

        if with_registration:
            new_bp._future_routes = list(self._future_routes)
            new_bp._future_middleware = list(self._future_middleware)
            new_bp._future_listeners = list(self._future_listeners)
            new_bp._future_exceptions = list(self._future_exceptions)
            new_bp._future_signals = list(self._future_signals)
            new_bp._future_statics = list(self._future_statics)

        if with_ctx:
            new_bp.ctx = self.ctx

        return new_bp

    @staticmethod
    def group(
        *blueprints: "Blueprint",
        url_prefix: Optional[str] = None,
        version: Optional[Union[int, str, float]] = None,
        strict_slashes: Optional[bool] = None,
        version_prefix: str = "/v",
    ) -> "BlueprintGroup":
        """Create a blueprint group."""
        from sanic.blueprint_group import BlueprintGroup

        return BlueprintGroup(
            url_prefix=url_prefix,
            version=version,
            strict_slashes=strict_slashes,
            version_prefix=version_prefix,
            blueprints=blueprints,
        )


__all__ = [
    "Blueprint",
]
