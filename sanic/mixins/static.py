"""Static files mixin."""
from pathlib import Path
from typing import Callable, Optional, Union


class StaticMixin:
    """Static file serving mixin."""

    __slots__ = ()

    def static(
        self,
        uri: str,
        file_or_directory: Union[str, Path],
        pattern: str = r"/?.+",
        use_modified_since: bool = True,
        use_content_range: bool = False,
        stream_large_files: bool = False,
        name: str = "static",
        host: Optional[str] = None,
        strict_slashes: Optional[bool] = None,
        content_type: Optional[str] = None,
        apply: bool = True,
        resource_type: Optional[str] = None,
        index: Optional[str] = None,
        directory_view: bool = False,
        directory_handler: Optional[Callable] = None,
    ):
        """Register static file route."""
        raise NotImplementedError
