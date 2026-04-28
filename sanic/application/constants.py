"""Sanic application constants."""
from enum import auto

from sanic.constants import StrEnum


class Mode(StrEnum):
    """Application mode."""

    PRODUCTION = auto()
    DEBUG = auto()


class Server(StrEnum):
    """Server type."""

    SANIC = auto()
    ASGI = auto()


class ServerStage:
    """Server stage values."""

    STOPPED = 0
    PARTIAL = 1
    SERVING = 2

    def __init__(self, value: int):
        self.value = value

    def __gt__(self, other) -> bool:
        if isinstance(other, ServerStage):
            return self.value > other.value
        return NotImplemented


ServerStage.STOPPED = ServerStage(0)
ServerStage.PARTIAL = ServerStage(1)
ServerStage.SERVING = ServerStage(2)


__all__ = [
    "Mode",
    "Server",
    "ServerStage",
]
