"""Content range handler."""
from typing import Any, Optional, Tuple


class ContentRangeHandler:
    """Handle content range requests."""

    def __init__(
        self,
        request: Any,
        total: int = 0,
        mime_type: Optional[str] = None,
    ):
        self.request = request
        self.total = total
        self.mime_type = mime_type
        self.start = 0
        self.end = total - 1 if total > 0 else 0
        self.size = total
        self.headers = {}

    def __bool__(self) -> bool:
        return self.total > 0
