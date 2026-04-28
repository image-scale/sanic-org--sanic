"""Handler types."""
from typing import Any, Awaitable, Callable, TypeVar, Union


RouteHandler = Callable[..., Union[Any, Awaitable[Any]]]
MiddlewareType = Callable[..., Union[Any, Awaitable[Any]]]
ErrorHandler = Callable[..., Union[Any, Awaitable[Any]]]
ListenerType = Callable[..., Union[Any, Awaitable[Any]]]
SignalHandler = Callable[..., Union[Any, Awaitable[Any]]]
