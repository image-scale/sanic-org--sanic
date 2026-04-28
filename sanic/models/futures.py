"""Future models for deferred registration."""
from dataclasses import dataclass, field
from typing import Any, Callable, FrozenSet, Iterable, Optional, Sequence, Type, Union


@dataclass
class FutureRoute:
    """Deferred route registration."""

    handler: Callable
    uri: str
    methods: Optional[FrozenSet[str]] = None
    host: Optional[str] = None
    strict_slashes: Optional[bool] = None
    stream: bool = False
    version: Optional[Union[int, str, float]] = None
    name: Optional[str] = None
    ignore_body: bool = False
    version_prefix: str = "/v"
    error_format: Optional[str] = None
    route_context: Any = None
    static: bool = False
    ctx_kwargs: dict = field(default_factory=dict)


@dataclass
class FutureMiddleware:
    """Deferred middleware registration."""

    middleware: Callable
    attach_to: str = "request"
    priority: int = 0


@dataclass
class FutureException:
    """Deferred exception handler registration."""

    handler: Callable
    exceptions: tuple


@dataclass
class FutureListener:
    """Deferred listener registration."""

    listener: Callable
    event: str


@dataclass
class FutureSignal:
    """Deferred signal registration."""

    handler: Callable
    event: str
    condition: Optional[dict] = None


@dataclass
class FutureStatic:
    """Deferred static file registration."""

    uri: str
    file_or_directory: str
    pattern: Optional[str] = None
    use_modified_since: bool = True
    use_content_range: bool = False
    stream_large_files: bool = False
    name: str = "static"
    host: Optional[str] = None
    strict_slashes: Optional[bool] = None
    content_type: Optional[str] = None
    resource_type: Optional[str] = None
    directory_view: bool = False
    directory_handler: Optional[Callable] = None


__all__ = [
    "FutureRoute",
    "FutureMiddleware",
    "FutureException",
    "FutureListener",
    "FutureSignal",
    "FutureStatic",
]
