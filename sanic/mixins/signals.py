"""Signals mixin."""
from typing import Any, Callable, Optional


class SignalMixin:
    """Signal registration mixin."""

    __slots__ = ()

    def signal(
        self,
        event: str,
        *,
        apply: bool = True,
        condition: Optional[dict] = None,
    ) -> Callable:
        """Register signal handler decorator."""

        def decorator(handler: Callable) -> Callable:
            self._apply_signal(handler, event, condition)
            return handler

        return decorator

    def _apply_signal(self, handler: Callable, event: str, condition: Optional[dict]):
        """Apply signal - to be implemented by subclass."""
        raise NotImplementedError

    def add_signal(
        self,
        handler: Callable,
        event: str,
        condition: Optional[dict] = None,
    ):
        """Add signal programmatically."""
        self._apply_signal(handler, event, condition)

    async def dispatch(
        self,
        event: str,
        *,
        context: Optional[dict] = None,
        condition: Optional[dict] = None,
        fail_not_found: bool = True,
        inline: bool = False,
        reverse: bool = False,
    ) -> Any:
        """Dispatch signal."""
        raise NotImplementedError

    def event(self, event: str):
        """Wait for event."""
        raise NotImplementedError
