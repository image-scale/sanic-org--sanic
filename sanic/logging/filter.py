"""Logging filters."""
import logging


class VerbosityFilter(logging.Filter):
    """Filter by verbosity level."""

    def __init__(self, verbosity: int = 0):
        super().__init__()
        self.verbosity = verbosity

    def filter(self, record):
        return True
