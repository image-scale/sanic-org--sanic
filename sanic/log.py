"""Sanic logging defaults."""
import warnings

from sanic.logging.default import LOGGING_CONFIG_DEFAULTS
from sanic.logging.loggers import (
    logger,
    error_logger,
    access_logger,
    server_logger,
)


class Colors:
    """ANSI color codes for terminal output."""

    END = "\033[0m"
    BOLD = "\033[1m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    SANIC = "\033[38;2;255;13;104m"


def deprecation(message: str, version: float = None):
    """Issue a deprecation warning."""
    warnings.warn(message, DeprecationWarning, stacklevel=2)


__all__ = [
    "Colors",
    "LOGGING_CONFIG_DEFAULTS",
    "deprecation",
    "logger",
    "error_logger",
    "access_logger",
    "server_logger",
]
