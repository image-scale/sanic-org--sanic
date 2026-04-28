"""Directory handler."""
from pathlib import Path
from typing import Any, Callable, Optional


class DirectoryHandler:
    """Handle directory listings."""

    def __init__(
        self,
        uri: str,
        directory: Path,
        directory_view: bool = False,
        index: Optional[str] = None,
    ):
        self.uri = uri
        self.directory = directory
        self.directory_view = directory_view
        self.index = index

    async def __call__(self, request: Any, path: str = "") -> Any:
        """Handle directory request."""
        raise NotImplementedError
