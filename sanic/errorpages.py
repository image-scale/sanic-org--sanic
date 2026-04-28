"""Sanic error pages."""
from typing import Any, Optional, Tuple


def exception_response(*args, **kwargs):
    """Generate exception response."""
    raise NotImplementedError


def guess_mime(accept_header: Optional[str], content_type: Optional[str] = None) -> Tuple[str, str]:
    """Guess MIME type from Accept header."""
    if content_type:
        return content_type, "text"
    if accept_header:
        if "text/html" in accept_header:
            return "text/html", "html"
        elif "application/json" in accept_header:
            return "application/json", "json"
    return "text/plain", "text"


class TextRenderer:
    """Text error renderer."""

    pass


class HTMLRenderer:
    """HTML error renderer."""

    pass


class JSONRenderer:
    """JSON error renderer."""

    pass


RENDERERS = {
    "text": TextRenderer,
    "html": HTMLRenderer,
    "json": JSONRenderer,
}


__all__ = [
    "exception_response",
    "guess_mime",
    "TextRenderer",
    "HTMLRenderer",
    "JSONRenderer",
    "RENDERERS",
]
