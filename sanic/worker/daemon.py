"""Daemon process."""
import os
from dataclasses import dataclass
from typing import Optional


class DaemonError(Exception):
    """Daemon error exception."""

    pass


@dataclass
class PidfileInfo:
    """Pidfile info."""

    path: str
    pid: int
    check: bool = True


def _get_default_runtime_dir() -> str:
    """Get default runtime directory."""
    return os.path.join(os.getcwd(), ".sanic")


def _is_sanic_process() -> bool:
    """Check if running in a Sanic process."""
    return os.environ.get("SANIC_WORKER_PROCESS") is not None


class Daemon:
    """Daemon process manager."""

    pass


__all__ = [
    "Daemon",
    "DaemonError",
    "PidfileInfo",
    "_get_default_runtime_dir",
    "_is_sanic_process",
]
