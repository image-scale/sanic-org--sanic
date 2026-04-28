"""Sanic application."""
from __future__ import annotations

import asyncio
import logging
import logging.config
import os
import re

from collections import deque
from functools import partial
from inspect import isawaitable
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
    Type,
    Union,
)

from sanic.application.state import ApplicationState
from sanic.base.root import BaseSanic
from sanic.blueprints import Blueprint
from sanic.config import Config
from sanic.exceptions import SanicException
from sanic.handlers.error import ErrorHandler
from sanic.helpers import Default, _default
from sanic.log import LOGGING_CONFIG_DEFAULTS
from sanic.logging.formatter import AutoFormatter
from sanic.mixins.exceptions import ExceptionMixin
from sanic.mixins.listeners import ListenerMixin
from sanic.mixins.middleware import MiddlewareMixin
from sanic.mixins.routes import RouteMixin
from sanic.mixins.signals import SignalMixin
from sanic.mixins.startup import StartupMixin, WebSocketProtocol, try_use_uvloop
from sanic.mixins.static import StaticMixin
from sanic.models.futures import (
    FutureException,
    FutureListener,
    FutureMiddleware,
    FutureRoute,
    FutureSignal,
)
from sanic.request import Request
from sanic.response import HTTPResponse, text as text_response
from sanic.router import Router
from sanic.signals import SignalGroup
from sanic.touchup.service import TouchUp


if TYPE_CHECKING:
    from sanic.server.async_server import AsyncioServer


class Sanic(
    BaseSanic,
    RouteMixin,
    MiddlewareMixin,
    ListenerMixin,
    ExceptionMixin,
    SignalMixin,
    StaticMixin,
    StartupMixin,
):
    """The Sanic application."""

    _app_registry: Dict[str, "Sanic"] = {}
    _uvloop_setting: Optional[Any] = None
    test_mode: bool = False

    __slots__ = (
        "_asgi_app",
        "_blueprint_order",
        "_future_exceptions",
        "_future_listeners",
        "_future_middleware",
        "_future_routes",
        "_future_signals",
        "_future_statics",
        "_loop",
        "_inspector",
        "_manager",
        "_state",
        "_test_manager",
        "asgi",
        "auto_reload",
        "blueprints",
        "config",
        "configure_logging",
        "ctx",
        "debug",
        "error_handler",
        "go_fast",
        "listeners",
        "multiplexer",
        "named_request_middleware",
        "named_response_middleware",
        "request_class",
        "request_middleware",
        "response_middleware",
        "router",
        "signal_router",
        "sock",
        "strict_slashes",
        "websocket_enabled",
        "websocket_tasks",
    )

    def __init__(
        self,
        name: str = None,
        config: Optional[Config] = None,
        ctx: Optional[Any] = None,
        router: Optional[Router] = None,
        signal_router: Optional[SignalGroup] = None,
        error_handler: Optional[ErrorHandler] = None,
        env_prefix: Optional[str] = "SANIC_",
        request_class: Optional[Type[Request]] = None,
        strict_slashes: bool = False,
        log_config: Optional[Dict[str, Any]] = None,
        configure_logging: bool = True,
        dumps: Optional[Callable] = None,
        loads: Optional[Callable] = None,
        inspector: bool = False,
        inspector_class: Optional[Type] = None,
        certloader_class: Optional[Type] = None,
    ):
        # Validate config and env_prefix combination
        if config is not None and env_prefix is not None and env_prefix != "SANIC_":
            raise SanicException(
                "When instantiating Sanic with config, you cannot also pass env_prefix"
            )

        super().__init__(name)

        # Configuration
        if config is None:
            config = Config(env_prefix=env_prefix)
        self.config = config

        # Update inspector config
        self.config.INSPECTOR = inspector

        # Context
        if ctx is not None:
            self.ctx = ctx

        # Router
        self.router = router or Router()
        self.router.ctx.app = self

        # Signal router
        self.signal_router = signal_router or SignalGroup()

        # Error handler
        self.error_handler = error_handler or ErrorHandler()

        # Request class
        self.request_class = request_class or Request

        # Settings
        self.strict_slashes = strict_slashes
        self.configure_logging = configure_logging

        # State
        self._state = ApplicationState()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._inspector = None
        self._manager = None
        self._test_manager = None
        self._asgi_app = None

        # Collections
        self.blueprints: Dict[str, Blueprint] = {}
        self._blueprint_order: List[Blueprint] = []
        self.listeners: Dict[str, List[Callable]] = {}
        self.request_middleware: deque = deque()
        self.response_middleware: deque = deque()
        self.named_request_middleware: Dict[str, deque] = {}
        self.named_response_middleware: Dict[str, deque] = {}
        self._future_routes: List[FutureRoute] = []
        self._future_middleware: List[FutureMiddleware] = []
        self._future_listeners: List[FutureListener] = []
        self._future_exceptions: List[FutureException] = []
        self._future_signals: List[FutureSignal] = []
        self._future_statics: List = []

        # WebSocket
        self.websocket_enabled = False
        self.websocket_tasks: Set = set()

        # Multiplexer
        self.multiplexer = None

        # Configure logging
        if configure_logging:
            if log_config is None:
                log_config = LOGGING_CONFIG_DEFAULTS
            logging.config.dictConfig(log_config)

        # Register app
        self.register_app(self)

    def __str__(self) -> str:
        return f"<Sanic {self.name}>"

    def __repr__(self) -> str:
        return f'Sanic(name="{self.name}")'

    def __setattr__(self, name: str, value: Any) -> None:
        # Prevent setting attributes on the app instance
        if name not in self.__slots__ and not name.startswith("_"):
            raise AttributeError(
                "Setting variables on Sanic instances is not allowed. You should "
                "change your Sanic instance to use instance.ctx.foo instead."
            )
        super().__setattr__(name, value)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Get event loop."""
        if self._loop is None:
            raise SanicException(
                "Loop can only be retrieved after the app has started "
                "running. Not supported with `create_server` function"
            )
        return self._loop

    @property
    def state(self) -> ApplicationState:
        """Get application state."""
        return self._state

    @property
    def manager(self) -> Any:
        """Get worker manager."""
        if self._manager is None or os.environ.get("SANIC_WORKER_PROCESS"):
            raise SanicException("Can only access the manager from the main process")
        return self._manager

    @property
    def inspector(self) -> Any:
        """Get inspector."""
        if self._inspector is None or os.environ.get("SANIC_WORKER_PROCESS"):
            raise SanicException("Can only access the inspector from the main process")
        return self._inspector

    @property
    def test_client(self):
        """Get test client."""
        from sanic_testing import TestManager

        if self._test_manager is None:
            self._test_manager = TestManager(self)
        return self._test_manager.test_client

    @property
    def asgi_client(self):
        """Get ASGI test client."""
        from sanic_testing import TestManager

        if self._test_manager is None:
            self._test_manager = TestManager(self)
        return self._test_manager.asgi_client

    @classmethod
    def register_app(cls, app: "Sanic") -> None:
        """Register app in the registry."""
        if not isinstance(app, cls):
            raise SanicException("Registered app must be an instance of Sanic")

        name = app.name
        if name in cls._app_registry and not cls.test_mode:
            raise SanicException(f'Sanic app name "{name}" already in use.')

        cls._app_registry[name] = app

    @classmethod
    def unregister_app(cls, app: "Sanic") -> None:
        """Unregister app from the registry."""
        cls._app_registry.pop(app.name, None)

    @classmethod
    def get_app(
        cls,
        name: Optional[str] = None,
        *,
        force_create: bool = False,
    ) -> "Sanic":
        """Get app by name."""
        if name is None:
            if len(cls._app_registry) == 0:
                raise SanicException("No Sanic apps have been registered.")
            if len(cls._app_registry) > 1:
                raise SanicException(
                    'Multiple Sanic apps found, use Sanic.get_app("app_name")'
                )
            return list(cls._app_registry.values())[0]

        try:
            return cls._app_registry[name]
        except KeyError:
            if force_create:
                return cls(name)
            raise SanicException(
                f"Sanic app name '{name}' not found.\n"
                "App instantiation must occur outside "
                "if __name__ == '__main__' "
                "block or by using an AppLoader.\nSee "
                "https://sanic.dev/en/guide/deployment/app-loader.html"
                " for more details."
            )

    def blueprint(
        self,
        blueprint: Union[Blueprint, Iterable[Blueprint]],
        **options: Any,
    ) -> None:
        """Register blueprint(s)."""
        if isinstance(blueprint, (list, tuple)):
            for bp in blueprint:
                self.blueprint(bp, **options)
            return

        if hasattr(blueprint, "blueprints"):
            # This is a BlueprintGroup
            for bp in blueprint:
                self.blueprint(bp, **options)
            return

        blueprint.register(self, options)
        self.blueprints[blueprint.name] = blueprint
        self._blueprint_order.append(blueprint)

        # Apply future registrations
        self._apply_blueprint(blueprint, **options)

    def _apply_blueprint(self, blueprint: Blueprint, **options: Any) -> None:
        """Apply blueprint routes/middleware/etc to app."""
        url_prefix = options.get("url_prefix", blueprint.url_prefix) or ""
        version = options.get("version", blueprint.version)
        version_prefix = options.get("version_prefix", blueprint.version_prefix)
        strict_slashes = options.get("strict_slashes", blueprint.strict_slashes)

        # Apply routes
        for future in blueprint._future_routes:
            uri = url_prefix + future.uri
            if version is not None:
                uri = f"{version_prefix}{version}{uri}"

            self._apply_route(
                future.handler,
                uri,
                future.methods or frozenset({"GET"}),
                future.host,
                strict_slashes if strict_slashes is not None else future.strict_slashes,
                future.stream,
                future.version or version,
                future.name,
                future.ignore_body,
                None,
                False,
                future.static,
                future.version_prefix or version_prefix,
                future.error_format,
                future.ctx_kwargs,
            )

        # Apply middleware
        for future in blueprint._future_middleware:
            self._apply_middleware(future.middleware, future.attach_to, future.priority)

        # Apply exception handlers
        for future in blueprint._future_exceptions:
            self._apply_exception_handler(future.exceptions, future.handler)

        # Apply listeners
        for future in blueprint._future_listeners:
            self._apply_listener(future.event, future.listener)

        # Apply signals
        for future in blueprint._future_signals:
            self._apply_signal(future.handler, future.event, future.condition)

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
        """Apply route to router."""
        route = self.router.add(
            uri=uri,
            methods=methods,
            handler=handler,
            host=host,
            strict_slashes=strict_slashes if strict_slashes is not None else self.strict_slashes,
            name=name,
            stream=stream,
            ignore_body=ignore_body,
            version=version,
            version_prefix=version_prefix,
            error_format=error_format,
            static=static,
            **ctx_kwargs,
        )

        # If websocket, enable it
        if websocket:
            self.websocket_enabled = True

        return route

    def _apply_middleware(self, middleware: Callable, attach_to: str, priority: int):
        """Apply middleware to app."""
        if attach_to == "request":
            self.request_middleware.append(middleware)
        elif attach_to == "response":
            self.response_middleware.appendleft(middleware)

    def _apply_listener(self, event: str, listener: Callable):
        """Apply listener to app."""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(listener)

    def _apply_exception_handler(self, exceptions, handler: Callable):
        """Apply exception handler to app."""
        if isinstance(exceptions[0], (list, tuple)):
            exceptions = exceptions[0]
        for exc in exceptions:
            self.error_handler.add(exc, handler)

    def _apply_signal(self, handler: Callable, event: str, condition: Optional[dict]):
        """Apply signal to app."""
        self.signal_router.add(event, handler, condition)

    def enable_websocket(self, enable: bool = True):
        """Enable websocket support."""
        self.websocket_enabled = enable

    def url_for(self, view_name: str, **kwargs) -> str:
        """Build URL for view."""
        raise NotImplementedError

    def _build_endpoint_name(self, *parts: str) -> str:
        """Build endpoint name."""
        return ".".join([self.name] + list(parts))

    def update_config(self, config: Union[Dict, str, Any]):
        """Update configuration."""
        self.config.update_config(config)

    def prepare(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        *,
        debug: bool = False,
        **kwargs,
    ):
        """Prepare server for running."""
        # Check proxy count
        if self.config.PROXIES_COUNT is not None and self.config.PROXIES_COUNT < 0:
            raise ValueError(
                "PROXIES_COUNT cannot be negative. "
                "https://sanic.readthedocs.io/en/latest/sanic/config.html"
                "#proxy-configuration"
            )

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        *,
        debug: bool = False,
        auto_reload: Optional[bool] = None,
        version: Any = None,
        ssl: Any = None,
        sock: Any = None,
        workers: int = 1,
        protocol: Any = None,
        backlog: int = 100,
        register_sys_signals: bool = True,
        access_log: Optional[bool] = None,
        unix: Optional[str] = None,
        loop: Any = None,
        reload_dir: Any = None,
        noisy_exceptions: Optional[bool] = None,
        motd: bool = True,
        fast: bool = False,
        verbosity: int = 0,
        motd_display: Optional[dict] = None,
        single_process: bool = False,
        auto_tls: bool = False,
        **kwargs,
    ):
        """Run the server."""
        if loop is not None:
            raise TypeError(
                "loop is not a valid argument. To use an existing loop, "
                "change to create_server().\nSee more: "
                "https://sanic.readthedocs.io/en/latest/sanic/deploying.html"
                "#asynchronous-support"
            )

        if fast and workers != 1:
            raise RuntimeError("You cannot use both fast=True and workers=X")

        if workers == 0:
            raise RuntimeError("Cannot serve with no workers")

        if single_process and (fast or workers != 1 or auto_reload):
            raise RuntimeError(
                "Single process cannot be run with multiple workers or auto-reload"
            )

        # Update config
        if access_log is not None:
            self.config.ACCESS_LOG = access_log

        # Use uvloop if available
        if not single_process:
            from sanic.compat import OS_IS_WINDOWS
            if not OS_IS_WINDOWS:
                try_use_uvloop()

        raise NotImplementedError("run() not fully implemented in scaffold")

    async def create_server(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        *,
        debug: bool = False,
        ssl: Any = None,
        sock: Any = None,
        protocol: Any = None,
        backlog: int = 100,
        access_log: Optional[bool] = None,
        unix: Optional[str] = None,
        return_asyncio_server: bool = False,
        asyncio_server_kwargs: Optional[dict] = None,
        noisy_exceptions: Optional[bool] = None,
    ) -> "AsyncioServer":
        """Create asyncio server."""
        from sanic.server.async_server import AsyncioServer

        # Update access log
        if access_log is not None:
            self.config.ACCESS_LOG = access_log

        # Check for main process listeners
        if "main_process_start" in self.listeners or "main_process_stop" in self.listeners:
            logging.getLogger("sanic.root").warning(
                "Listener events for the main process are not available with "
                "create_server()"
            )

        # Check uvloop configuration
        if not isinstance(self.config.USE_UVLOOP, Default):
            logging.getLogger("sanic.root").warning(
                "You are trying to change the uvloop configuration, but "
                "this is only effective when using the run(...) method. "
                "When using the create_server(...) method Sanic will use "
                "the already existing loop."
            )

        # Check multiple uvloop configurations
        if Sanic._uvloop_setting is not None:
            if Sanic._uvloop_setting != self.config.USE_UVLOOP:
                logging.getLogger("sanic.root").warning(
                    "It looks like you're running several apps with different "
                    "uvloop settings. This is not supported and may lead to "
                    "unintended behaviour."
                )
        Sanic._uvloop_setting = self.config.USE_UVLOOP

        host = host or "127.0.0.1"
        port = port or 8000

        # Finalize router
        self.router.finalize()

        # Create server
        loop = asyncio.get_event_loop()
        connections = set()
        asyncio_server_kwargs = asyncio_server_kwargs or {}

        server_coroutine = loop.create_server(
            lambda: protocol if protocol else self._create_protocol(),
            host=host,
            port=port,
            ssl=ssl,
            backlog=backlog,
            **asyncio_server_kwargs,
        )

        server = AsyncioServer(
            app=self,
            loop=loop,
            serve_coro=server_coroutine,
            connections=connections,
        )

        if return_asyncio_server:
            server._server = await server_coroutine
            return server

        return server

    def _create_protocol(self):
        """Create HTTP protocol."""
        from sanic.server.protocols.http_protocol import HttpProtocol

        return HttpProtocol(app=self)

    def stop(self, terminate: bool = True, unregister: bool = False):
        """Stop the server."""
        if self.multiplexer:
            self.multiplexer.terminate()

        if terminate:
            Sanic._app_registry.clear()
        elif unregister:
            Sanic._app_registry.pop(self.name, None)

    @classmethod
    def serve(cls, *args, **kwargs):
        """Serve multiple apps."""
        raise NotImplementedError

    def refresh(self, passthru: Optional[dict] = None) -> "Sanic":
        """Refresh app with passthru data."""
        if passthru:
            for key, value in passthru.items():
                if key == "config":
                    for config_key, config_value in value.items():
                        setattr(self.config, config_key, config_value)
                else:
                    setattr(self, key, value)
        return self

    async def handle_request(self, request: Request) -> HTTPResponse:
        """Handle incoming request."""
        raise NotImplementedError

    async def dispatch(
        self,
        event: str,
        *,
        context: Optional[dict] = None,
        condition: Optional[dict] = None,
        fail_not_found: bool = True,
        inline: bool = False,
        reverse: bool = False,
    ):
        """Dispatch signal."""
        await self.signal_router.dispatch(event, context, condition)


# Re-exports
__all__ = [
    "Sanic",
]
