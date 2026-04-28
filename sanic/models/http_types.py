"""HTTP types."""
from typing import Any


class Range:
    """HTTP range type."""

    def __init__(self, start: int, end: int, size: int, total: int):
        self.start = start
        self.end = end
        self.size = size
        self.total = total
