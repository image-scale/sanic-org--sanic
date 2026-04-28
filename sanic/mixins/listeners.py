"""Listeners mixin."""
from functools import partial
from typing import Callable, Optional


class ListenerMixin:
    """Listener registration mixin."""

    __slots__ = ()

    def listener(
        self,
        listener_or_event: Optional[Callable] = None,
        event: Optional[str] = None,
    ) -> Callable:
        """Register listener decorator."""

        def decorator(listener: Callable) -> Callable:
            self._apply_listener(event, listener)
            return listener

        if callable(listener_or_event):
            return decorator(listener_or_event)

        if listener_or_event is not None:
            event = listener_or_event

        return decorator

    def _apply_listener(self, event: str, listener: Callable):
        """Apply listener - to be implemented by subclass."""
        raise NotImplementedError

    def before_server_start(self, listener: Callable = None) -> Callable:
        """Register before server start listener."""
        return self.listener(listener, "before_server_start")

    def after_server_start(self, listener: Callable = None) -> Callable:
        """Register after server start listener."""
        return self.listener(listener, "after_server_start")

    def before_server_stop(self, listener: Callable = None) -> Callable:
        """Register before server stop listener."""
        return self.listener(listener, "before_server_stop")

    def after_server_stop(self, listener: Callable = None) -> Callable:
        """Register after server stop listener."""
        return self.listener(listener, "after_server_stop")

    def main_process_start(self, listener: Callable = None) -> Callable:
        """Register main process start listener."""
        return self.listener(listener, "main_process_start")

    def main_process_stop(self, listener: Callable = None) -> Callable:
        """Register main process stop listener."""
        return self.listener(listener, "main_process_stop")

    def before_reload_trigger(self, listener: Callable = None) -> Callable:
        """Register before reload trigger listener."""
        return self.listener(listener, "before_reload_trigger")

    def after_reload_trigger(self, listener: Callable = None) -> Callable:
        """Register after reload trigger listener."""
        return self.listener(listener, "after_reload_trigger")

    def reload_process_start(self, listener: Callable = None) -> Callable:
        """Register reload process start listener."""
        return self.listener(listener, "reload_process_start")

    def reload_process_stop(self, listener: Callable = None) -> Callable:
        """Register reload process stop listener."""
        return self.listener(listener, "reload_process_stop")
