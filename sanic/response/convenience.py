"""Response convenience functions."""
from __future__ import annotations

import mimetypes
import os

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    Callable,
    Coroutine,
    Dict,
    Optional,
    Union,
)

from sanic.compat import Header
from sanic.response.types import HTTPResponse, ResponseStream


try:
    import ujson as json_module

    def json_dumps(obj: Any, **kwargs) -> str:
        return json_module.dumps(obj, **kwargs)
except ImportError:
    import json as json_module

    def json_dumps(obj: Any, **kwargs) -> str:
        return json_module.dumps(obj, **kwargs)


def guess_content_type(path: str) -> str:
    """Guess content type from file path."""
    mime_type, _ = mimetypes.guess_type(path)
    return mime_type or "application/octet-stream"


def empty(
    status: int = 204,
    headers: Optional[Dict[str, str]] = None,
) -> HTTPResponse:
    """Create empty response."""
    return HTTPResponse(
        body=b"",
        status=status,
        headers=headers,
        content_type=None,
    )


def text(
    body: str,
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "text/plain; charset=utf-8",
) -> HTTPResponse:
    """Create text response."""
    return HTTPResponse(
        body=body,
        status=status,
        headers=headers,
        content_type=content_type,
    )


def html(
    body: str,
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
) -> HTTPResponse:
    """Create HTML response."""
    return HTTPResponse(
        body=body,
        status=status,
        headers=headers,
        content_type="text/html; charset=utf-8",
    )


def json(
    body: Any,
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "application/json",
    dumps: Callable = None,
    **kwargs,
) -> HTTPResponse:
    """Create JSON response."""
    if dumps is None:
        dumps = json_dumps
    return HTTPResponse(
        body=dumps(body, **kwargs),
        status=status,
        headers=headers,
        content_type=content_type,
    )


def raw(
    body: Optional[bytes],
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "application/octet-stream",
) -> HTTPResponse:
    """Create raw bytes response."""
    return HTTPResponse(
        body=body,
        status=status,
        headers=headers,
        content_type=content_type,
    )


def redirect(
    to: str,
    headers: Optional[Dict[str, str]] = None,
    status: int = 302,
    content_type: str = "text/html; charset=utf-8",
) -> HTTPResponse:
    """Create redirect response."""
    safe_to = to.replace("\r", "").replace("\n", "")
    headers = headers or {}
    headers["Location"] = safe_to
    return HTTPResponse(
        body=b"",
        status=status,
        headers=headers,
        content_type=content_type,
    )


async def file(
    location: Union[str, Path],
    status: int = 200,
    mime_type: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    filename: Optional[str] = None,
    _range: Optional[Any] = None,
) -> HTTPResponse:
    """Create file response."""
    raise NotImplementedError


async def file_stream(
    location: Union[str, Path],
    status: int = 200,
    chunk_size: int = 4096,
    mime_type: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    filename: Optional[str] = None,
    _range: Optional[Any] = None,
) -> ResponseStream:
    """Create streaming file response."""
    raise NotImplementedError


def validate_file(location: Union[str, Path]) -> Path:
    """Validate that a file exists and return its Path."""
    path = Path(location)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {location}")
    if not path.is_file():
        raise ValueError(f"Not a file: {location}")
    return path


__all__ = [
    "empty",
    "file",
    "file_stream",
    "guess_content_type",
    "html",
    "json",
    "json_dumps",
    "raw",
    "redirect",
    "text",
    "validate_file",
]
