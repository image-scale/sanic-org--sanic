"""Application state management."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

from sanic.application.constants import Mode, Server, ServerStage


@dataclass
class ApplicationState:
    """Application state."""

    app_name: str = ""
    is_started: bool = False
    is_stopping: bool = False
    is_running: bool = False
    stage: ServerStage = field(default_factory=lambda: ServerStage.STOPPED)
    mode: Mode = Mode.PRODUCTION
    server: Server = Server.SANIC
    reload_dirs: Set[str] = field(default_factory=set)
    fast: bool = False
    verbosity: int = 0

    @property
    def is_debug(self) -> bool:
        return self.mode == Mode.DEBUG


@dataclass
class ApplicationServerInfo:
    """Server info for application state."""

    settings: Dict[str, Any] = field(default_factory=dict)
    state: str = ""


__all__ = [
    "ApplicationServerInfo",
    "ApplicationState",
]
