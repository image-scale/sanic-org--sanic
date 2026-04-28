"""Hashable dictionary."""
from typing import Any, Dict


class HashableDict(dict):
    """Dictionary that can be hashed."""

    def __hash__(self):
        return hash(tuple(sorted(self.items())))
