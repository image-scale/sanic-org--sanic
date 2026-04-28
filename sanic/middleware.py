"""Sanic middleware."""
from enum import IntEnum
from typing import Callable


class MiddlewareLocation(IntEnum):
    """Middleware location."""

    REQUEST = 0
    RESPONSE = 1


class Middleware:
    """Middleware wrapper."""

    def __init__(
        self,
        func: Callable,
        location: MiddlewareLocation = MiddlewareLocation.REQUEST,
        priority: int = 0,
    ):
        self.func = func
        self.location = location
        self.priority = priority

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


__all__ = [
    "Middleware",
    "MiddlewareLocation",
]
