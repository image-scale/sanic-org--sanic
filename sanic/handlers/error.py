"""Error handler."""
from typing import Any, Callable, Dict, Optional, Type, Union

from sanic.exceptions import SanicException


class ErrorHandler:
    """Handle exceptions and error responses."""

    def __init__(self, fallback: str = "auto"):
        self.cached_handlers: Dict[Type[Exception], Callable] = {}
        self.fallback = fallback

    def add(self, exception: Type[Exception], handler: Callable):
        """Add exception handler."""
        self.cached_handlers[exception] = handler

    def lookup(
        self,
        exception: Exception,
        route_name: Optional[str] = None,
    ) -> Optional[Callable]:
        """Look up handler for exception."""
        for exc_type, handler in self.cached_handlers.items():
            if isinstance(exception, exc_type):
                return handler
        return None

    def response(self, request: Any, exception: Exception) -> Any:
        """Generate error response."""
        raise NotImplementedError

    def default(self, request: Any, exception: Exception) -> Any:
        """Default error handler."""
        raise NotImplementedError

    def _lookup_exception(self, exception: Exception) -> Optional[Callable]:
        """Look up exception handler."""
        return self.lookup(exception)
