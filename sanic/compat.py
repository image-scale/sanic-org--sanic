"""Sanic compatibility helpers."""
import asyncio
import os
import signal
import sys
from contextvars import ContextVar

from multidict import CIMultiDict


OS_IS_WINDOWS = sys.platform in ["win32", "cygwin"]

Header = CIMultiDict

# Check for uvloop
try:
    import uvloop
    UVLOOP_INSTALLED = True
except ImportError:
    UVLOOP_INSTALLED = False


def enable_traceback_filter():
    """Enable traceback filtering."""
    pass


def stat_async(path):
    """Async stat - stub."""
    raise NotImplementedError


def ctrlc_workaround_for_windows(app):
    """Workaround for Ctrl+C on Windows."""
    if OS_IS_WINDOWS:
        signal.signal(signal.SIGINT, signal.SIG_DFL)


def use_context(func):
    """Use context decorator - stub."""
    return func


__all__ = [
    "OS_IS_WINDOWS",
    "Header",
    "UVLOOP_INSTALLED",
    "enable_traceback_filter",
    "stat_async",
    "ctrlc_workaround_for_windows",
    "use_context",
]
