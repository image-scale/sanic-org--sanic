"""Middleware mixin."""
from functools import partial
from typing import Callable, Optional, Union


class MiddlewareMixin:
    """Middleware registration mixin."""

    __slots__ = ()

    def middleware(
        self,
        middleware_or_request: Optional[Union[Callable, str]] = None,
        attach_to: str = "request",
        apply: bool = True,
        *,
        priority: int = 0,
    ) -> Callable:
        """Register middleware decorator."""

        def decorator(middleware: Callable) -> Callable:
            self._apply_middleware(middleware, attach_to, priority)
            return middleware

        if callable(middleware_or_request):
            return decorator(middleware_or_request)

        if middleware_or_request is not None:
            attach_to = middleware_or_request

        return decorator

    def _apply_middleware(self, middleware: Callable, attach_to: str, priority: int):
        """Apply middleware - to be implemented by subclass."""
        raise NotImplementedError

    def on_request(self, middleware: Callable = None, priority: int = 0) -> Callable:
        """Register request middleware."""
        return self.middleware(middleware, "request", priority=priority)

    def on_response(self, middleware: Callable = None, priority: int = 0) -> Callable:
        """Register response middleware."""
        return self.middleware(middleware, "response", priority=priority)
