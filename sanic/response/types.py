"""Response types."""
from __future__ import annotations

from http.cookies import SimpleCookie
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from sanic.compat import Header
from sanic.cookies.response import CookieJar


class BaseHTTPResponse:
    """Base HTTP response class."""

    status: int = 200
    content_type: Optional[str] = None
    _headers: Header
    _cookies: Optional[CookieJar] = None
    body: Optional[bytes] = None
    stream: Any = None


class HTTPResponse(BaseHTTPResponse):
    """HTTP response object."""

    __slots__ = (
        "body",
        "status",
        "content_type",
        "_headers",
        "_cookies",
        "stream",
    )

    def __init__(
        self,
        body: Optional[Union[str, bytes]] = None,
        status: int = 200,
        headers: Optional[Union[Dict[str, str], Header]] = None,
        content_type: Optional[str] = None,
    ):
        if body is not None:
            if isinstance(body, str):
                self.body = body.encode("utf-8")
            else:
                self.body = body
        else:
            self.body = b""

        self.status = status
        self.content_type = content_type
        self._cookies: Optional[CookieJar] = None
        self.stream = None

        if headers:
            if isinstance(headers, Header):
                self._headers = headers
            else:
                self._headers = Header(headers)
        else:
            self._headers = Header()

    @property
    def headers(self) -> Header:
        """Get headers."""
        return self._headers

    @property
    def cookies(self) -> CookieJar:
        """Get cookies."""
        if self._cookies is None:
            self._cookies = CookieJar(self._headers)
        return self._cookies

    def add_cookie(self, *args, **kwargs):
        """Add cookie."""
        return self.cookies.add_cookie(*args, **kwargs)

    def delete_cookie(self, *args, **kwargs):
        """Delete cookie."""
        return self.cookies.delete_cookie(*args, **kwargs)

    @property
    def processed_headers(self) -> Iterable[Tuple[str, str]]:
        """Get processed headers."""
        headers = []

        # Content-Type
        if self.content_type:
            headers.append(("content-type", self.content_type))

        # Content-Length
        if self.body:
            headers.append(("content-length", str(len(self.body))))

        # Custom headers
        for key, value in self._headers.items():
            headers.append((key.lower(), str(value)))

        # Cookies
        if self._cookies:
            for cookie in self._cookies.values():
                headers.append(("set-cookie", cookie.encode()))

        return headers


class ResponseStream:
    """Streaming response object."""

    def __init__(
        self,
        streaming_fn: Any,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
    ):
        self.streaming_fn = streaming_fn
        self.status = status
        self.headers = headers or {}
        self.content_type = content_type

    async def send(self, data: bytes):
        """Send data chunk."""
        raise NotImplementedError

    async def eof(self):
        """End stream."""
        raise NotImplementedError


class JSONResponse(HTTPResponse):
    """JSON response object."""

    def __init__(
        self,
        body: Any = None,
        status: int = 200,
        headers: Optional[Union[Dict[str, str], Header]] = None,
        content_type: str = "application/json",
        dumps: Any = None,
        **kwargs,
    ):
        import json as stdlib_json
        dumps = dumps or stdlib_json.dumps
        super().__init__(
            body=dumps(body) if body is not None else None,
            status=status,
            headers=headers,
            content_type=content_type,
        )


__all__ = [
    "BaseHTTPResponse",
    "HTTPResponse",
    "JSONResponse",
    "ResponseStream",
]
