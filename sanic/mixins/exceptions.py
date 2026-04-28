"""Exceptions mixin."""
from typing import Callable, Sequence, Type, Union


class ExceptionMixin:
    """Exception handler mixin."""

    __slots__ = ()

    def exception(
        self,
        *exceptions: Union[Type[Exception], Sequence[Type[Exception]]],
    ) -> Callable:
        """Register exception handler decorator."""

        def decorator(handler: Callable) -> Callable:
            self._apply_exception_handler(exceptions, handler)
            return handler

        return decorator

    def _apply_exception_handler(self, exceptions, handler):
        """Apply exception handler - to be implemented by subclass."""
        raise NotImplementedError
