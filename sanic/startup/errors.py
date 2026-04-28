"""Startup errors."""
import errno


class StartupFailure(Exception):
    """Startup failure exception."""

    pass


def _handle_os_error(exc: OSError) -> str:
    """Handle OS error and return a user-friendly message."""
    if exc.errno == errno.EADDRINUSE:
        return f"Address already in use: {exc}"
    elif exc.errno == errno.EACCES:
        return f"Permission denied: {exc}"
    elif exc.errno == errno.ENOENT:
        return f"File not found: {exc}"
    return str(exc)


def _handle_server_error(exc: Exception) -> str:
    """Handle server error and return a user-friendly message."""
    if isinstance(exc, OSError):
        return _handle_os_error(exc)
    return str(exc)


def maybe_handle_startup_error(exc: Exception) -> None:
    """Maybe handle startup error."""
    pass


__all__ = [
    "StartupFailure",
    "_handle_os_error",
    "_handle_server_error",
    "maybe_handle_startup_error",
]
