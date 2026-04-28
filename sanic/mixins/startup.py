"""Startup mixin."""
from typing import Any, Callable, Optional


def try_use_uvloop():
    """Try to use uvloop as event loop policy."""
    try:
        import uvloop
        import asyncio
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass


class WebSocketProtocol:
    """Stub for WebSocketProtocol."""

    def __init__(self, *args, **kwargs):
        pass


class StartupMixin:
    """Startup mixin for running the server."""

    __slots__ = ()

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
        raise NotImplementedError

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
    ):
        """Create asyncio server."""
        raise NotImplementedError

    def prepare(
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
    ):
        """Prepare server for running."""
        raise NotImplementedError

    @classmethod
    def serve(cls, *args, **kwargs):
        """Serve applications."""
        raise NotImplementedError

    def stop(self, terminate: bool = True, unregister: bool = False):
        """Stop the server."""
        raise NotImplementedError
