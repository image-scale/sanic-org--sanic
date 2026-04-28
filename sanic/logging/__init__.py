"""Sanic logging package."""
from sanic.logging.formatter import AutoFormatter
from sanic.logging.setup import setup_logging


__all__ = [
    "AutoFormatter",
    "setup_logging",
]
