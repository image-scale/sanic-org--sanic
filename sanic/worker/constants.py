"""Worker constants."""
from enum import auto, Enum


WORKER_PROCESS = "SANIC_WORKER_PROCESS"


class ProcessState(Enum):
    """Worker process state."""

    IDLE = auto()
    STARTING = auto()
    STARTED = auto()
    ACKED = auto()
    JOINED = auto()
    TERMINATED = auto()
    RESTARTING = auto()
    FAILED = auto()
    COMPLETED = auto()


class RestartOrder(Enum):
    """Worker restart order."""

    SHUTDOWN_FIRST = auto()
    STARTUP_FIRST = auto()


__all__ = [
    "ProcessState",
    "RestartOrder",
    "WORKER_PROCESS",
]
