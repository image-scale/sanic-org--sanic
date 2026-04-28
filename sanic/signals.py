"""Sanic signals."""
from enum import auto
from typing import Any, Callable, Dict, List, Optional


class Event:
    """Signal event constants."""

    SERVER_INIT_BEFORE = "server.init.before"
    SERVER_INIT_AFTER = "server.init.after"
    SERVER_SHUTDOWN_BEFORE = "server.shutdown.before"
    SERVER_SHUTDOWN_AFTER = "server.shutdown.after"
    HTTP_LIFECYCLE_BEGIN = "http.lifecycle.begin"
    HTTP_LIFECYCLE_COMPLETE = "http.lifecycle.complete"
    HTTP_LIFECYCLE_EXCEPTION = "http.lifecycle.exception"
    HTTP_LIFECYCLE_HANDLE = "http.lifecycle.handle"
    HTTP_LIFECYCLE_REQUEST = "http.lifecycle.request"
    HTTP_LIFECYCLE_RESPONSE = "http.lifecycle.response"
    HTTP_ROUTING_BEFORE = "http.routing.before"
    HTTP_ROUTING_AFTER = "http.routing.after"
    HTTP_MIDDLEWARE_BEFORE = "http.middleware.before"
    HTTP_MIDDLEWARE_AFTER = "http.middleware.after"


class Signal:
    """Signal class."""

    def __init__(self, name: str):
        self.name = name
        self.handlers: List[Callable] = []

    def add(self, handler: Callable):
        """Add handler."""
        self.handlers.append(handler)


class SignalGroup:
    """Signal group."""

    def __init__(self):
        self.signals: Dict[str, Signal] = {}

    def add(self, event: str, handler: Callable, condition: Optional[dict] = None):
        """Add signal handler."""
        if event not in self.signals:
            self.signals[event] = Signal(event)
        self.signals[event].add(handler)

    def reset(self):
        """Reset all signals."""
        self.signals.clear()

    def finalize(self):
        """Finalize signals."""
        pass

    async def dispatch(
        self,
        event: str,
        context: Optional[dict] = None,
        condition: Optional[dict] = None,
    ):
        """Dispatch signal."""
        if event in self.signals:
            for handler in self.signals[event].handlers:
                result = handler(**context) if context else handler()
                if hasattr(result, "__await__"):
                    await result


RESERVED_NAMESPACES = {"server", "http"}


__all__ = [
    "Event",
    "Signal",
    "SignalGroup",
    "RESERVED_NAMESPACES",
]
