"""Request parameters."""
from typing import Any, List, Optional


class RequestParameters(dict):
    """Multi-value dictionary for request parameters."""

    def getlist(self, key: str, default: Optional[List] = None) -> List[Any]:
        """Get all values for key."""
        return super().get(key, default or [])

    def get(self, key: str, default: Any = None) -> Any:
        """Get single value for key."""
        values = super().get(key)
        if values:
            return values[0] if isinstance(values, list) else values
        return default

    def __getitem__(self, key: str) -> Any:
        values = super().__getitem__(key)
        return values[0] if isinstance(values, list) and values else values
