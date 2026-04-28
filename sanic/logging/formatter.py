"""Sanic log formatters."""
import logging
import os


class AutoFormatter(logging.Formatter):
    """Auto-formatting log formatter."""

    SETUP = False
    LOG_EXTRA = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        return super().format(record)


class DebugAccessFormatter(logging.Formatter):
    """Debug access log formatter."""

    def format(self, record):
        return super().format(record)


class DebugFormatter(logging.Formatter):
    """Debug formatter."""

    def format(self, record):
        return super().format(record)


class ProdAccessFormatter(logging.Formatter):
    """Production access log formatter."""

    def format(self, record):
        return super().format(record)


class ProdFormatter(logging.Formatter):
    """Production formatter."""

    def format(self, record):
        return super().format(record)


__all__ = [
    "AutoFormatter",
    "DebugAccessFormatter",
    "DebugFormatter",
    "ProdAccessFormatter",
    "ProdFormatter",
]
