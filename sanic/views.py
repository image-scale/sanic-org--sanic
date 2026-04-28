"""Class-based views."""
from functools import wraps
from typing import Any, Callable, List, Optional, Set


def stream(func: Callable) -> Callable:
    """Decorator to mark a handler as streaming."""
    func.is_stream = True
    return func


class HTTPMethodView:
    """HTTP method view base class."""

    decorators: List[Callable] = []

    def dispatch_request(self, request, *args, **kwargs):
        """Dispatch request to appropriate handler."""
        method = request.method.lower()
        handler = getattr(self, method, None)
        if handler is None:
            raise NotImplementedError(f"Method {method} not implemented")
        return handler(request, *args, **kwargs)

    @classmethod
    def as_view(cls, *class_args, **class_kwargs) -> Callable:
        """Create view function from class."""

        def view(*args, **kwargs):
            instance = cls(*class_args, **class_kwargs)
            return instance.dispatch_request(*args, **kwargs)

        for decorator in cls.decorators:
            view = decorator(view)

        view.view_class = cls
        view.__name__ = cls.__name__
        view.__doc__ = cls.__doc__

        return view


class CompositionView:
    """Composition view."""

    def __init__(self):
        self.handlers = {}

    def add(self, methods: List[str], handler: Callable, stream: bool = False):
        """Add handler for methods."""
        for method in methods:
            self.handlers[method.upper()] = handler

    def __call__(self, request, *args, **kwargs):
        method = request.method.upper()
        handler = self.handlers.get(method)
        if handler is None:
            raise NotImplementedError(f"Method {method} not implemented")
        return handler(request, *args, **kwargs)


__all__ = [
    "CompositionView",
    "HTTPMethodView",
    "stream",
]
