"""Request types."""
from __future__ import annotations

import asyncio

from contextvars import ContextVar
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Optional,
    TypeVar,
    Union,
)
from urllib.parse import parse_qs, unquote, urlparse
from uuid import UUID, uuid4

from sanic.compat import Header
from sanic.constants import CACHEABLE_METHODS, IDEMPOTENT_METHODS, SAFE_METHODS
from sanic.cookies.request import CookieRequestParameters
from sanic.exceptions import BadURL, SanicException
from sanic.headers import AcceptList
from sanic.request.parameters import RequestParameters


if TYPE_CHECKING:
    from sanic.app import Sanic
    from sanic.server.protocols.http_protocol import HttpProtocol


_current_request: ContextVar[Optional["Request"]] = ContextVar(
    "current_request", default=None
)


SanicVar = TypeVar("SanicVar", bound="Sanic")
CtxVar = TypeVar("CtxVar")


class SimpleNamespace:
    """Simple namespace for request context."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Request(Generic[SanicVar, CtxVar]):
    """HTTP request object."""

    __slots__ = (
        "_id",
        "_name",
        "_parsed_url",
        "_cookies",
        "_match_info",
        "_body",
        "_json",
        "_form",
        "_files",
        "_args",
        "_accept",
        "_headers",
        "_method",
        "_app",
        "_protocol",
        "_stream",
        "_conn_info",
        "_route",
        "ctx",
        "raw_url",
        "responded",
        "request_middleware_started",
        "transport",
    )

    def __init__(
        self,
        url_bytes: bytes,
        headers: Header,
        version: Optional[str],
        method: str,
        transport: Any,
        app: Optional[SanicVar],
        head: bytes = b"",
        stream_id: int = 0,
    ):
        self.raw_url = url_bytes
        self._id: Optional[Union[UUID, str, int]] = None
        self._name: Optional[str] = None
        self._parsed_url: Optional[Any] = None
        self._cookies: Optional[CookieRequestParameters] = None
        self._match_info: Optional[Dict[str, Any]] = {}
        self._body: Optional[bytes] = None
        self._json: Any = None
        self._form: Optional[RequestParameters] = None
        self._files: Optional[RequestParameters] = None
        self._args: Optional[RequestParameters] = None
        self._accept: Optional[AcceptList] = None
        self._headers = headers or Header()
        self._method = method
        self._app = app
        self._protocol: Optional[HttpProtocol] = None
        self._stream: Any = None
        self._conn_info: Optional[Any] = None
        self._route: Any = None
        self.ctx = self.make_context()
        self.responded = False
        self.request_middleware_started = False
        self.transport = transport

        # Parse URL
        if url_bytes:
            try:
                url_string = url_bytes.decode("utf-8")
                if not url_string.startswith(("/", "http://", "https://")):
                    raise ValueError(f"Bad URL: {url_string}")
                self._parsed_url = urlparse(url_string)
            except Exception as e:
                raise BadURL(f"Bad URL: {url_bytes.decode('utf-8', errors='replace')}")

        # Set current request context
        _current_request.set(self)

    @staticmethod
    def make_context() -> CtxVar:
        """Create request context."""
        return SimpleNamespace()

    @classmethod
    def get_current(cls) -> "Request":
        """Get current request."""
        request = _current_request.get()
        if request is None:
            raise SanicException("No current request")
        return request

    @classmethod
    def generate_id(cls, request: "Request") -> UUID:
        """Generate request ID."""
        return uuid4()

    @property
    def id(self) -> Union[UUID, str, int]:
        """Get request ID."""
        if self._id is None:
            if self._app:
                header_name = self._app.config.REQUEST_ID_HEADER
                if header_name and header_name in self._headers:
                    raw_id = self._headers.get(header_name)
                    try:
                        self._id = int(raw_id)
                    except ValueError:
                        try:
                            self._id = UUID(raw_id)
                        except ValueError:
                            self._id = raw_id
                else:
                    self._id = self.generate_id(self)
            else:
                self._id = self.generate_id(self)
        return self._id

    @property
    def app(self) -> SanicVar:
        """Get app."""
        return self._app

    @property
    def name(self) -> Optional[str]:
        """Get route name."""
        if self._name:
            return self._name
        if self._route:
            return self._route.name
        return None

    @property
    def method(self) -> str:
        """Get HTTP method."""
        return self._method

    @property
    def headers(self) -> Header:
        """Get headers."""
        return self._headers

    @property
    def path(self) -> str:
        """Get path."""
        if self._parsed_url:
            return unquote(self._parsed_url.path or "/")
        return "/"

    @property
    def url(self) -> str:
        """Get full URL."""
        return self.raw_url.decode("utf-8") if isinstance(self.raw_url, bytes) else self.raw_url

    @property
    def query_string(self) -> str:
        """Get query string."""
        if self._parsed_url:
            return self._parsed_url.query or ""
        return ""

    @property
    def args(self) -> RequestParameters:
        """Get query arguments."""
        if self._args is None:
            self._args = RequestParameters()
            for k, v in parse_qs(self.query_string).items():
                self._args[k] = v
        return self._args

    @property
    def cookies(self) -> CookieRequestParameters:
        """Get cookies."""
        if self._cookies is None:
            cookie_header = self._headers.get("cookie", "")
            self._cookies = CookieRequestParameters(cookie_header)
        return self._cookies

    @property
    def body(self) -> Optional[bytes]:
        """Get body."""
        return self._body

    @body.setter
    def body(self, value: bytes):
        """Set body."""
        self._body = value

    @property
    def json(self) -> Any:
        """Get JSON body."""
        if self._json is None and self._body:
            import json
            self._json = json.loads(self._body)
        return self._json

    @property
    def form(self) -> RequestParameters:
        """Get form data."""
        if self._form is None:
            self._form = RequestParameters()
        return self._form

    @property
    def files(self) -> RequestParameters:
        """Get uploaded files."""
        if self._files is None:
            self._files = RequestParameters()
        return self._files

    @property
    def accept(self) -> AcceptList:
        """Get Accept header."""
        if self._accept is None:
            self._accept = AcceptList(self._headers.get("accept", ""))
        return self._accept

    @property
    def route(self) -> Any:
        """Get route."""
        return self._route

    @route.setter
    def route(self, value):
        """Set route."""
        self._route = value

    @property
    def match_info(self) -> Dict[str, Any]:
        """Get match info."""
        return self._match_info or {}

    @match_info.setter
    def match_info(self, value):
        """Set match info."""
        self._match_info = value

    @property
    def protocol(self) -> "HttpProtocol":
        """Get protocol."""
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        """Set protocol."""
        self._protocol = value

    @property
    def stream(self) -> Any:
        """Get stream."""
        return self._stream

    @stream.setter
    def stream(self, value):
        """Set stream."""
        self._stream = value

    @property
    def conn_info(self) -> Any:
        """Get connection info."""
        return self._conn_info

    @conn_info.setter
    def conn_info(self, value):
        """Set connection info."""
        self._conn_info = value

    @property
    def ip(self) -> str:
        """Get client IP."""
        if self._conn_info:
            return self._conn_info.client_ip
        return ""

    @property
    def port(self) -> Optional[int]:
        """Get client port."""
        if self._conn_info:
            return self._conn_info.client_port
        return None

    @property
    def server_port(self) -> Optional[int]:
        """Get server port."""
        if self._conn_info:
            return self._conn_info.server_port
        return None

    @property
    def host(self) -> str:
        """Get host."""
        return self._headers.get("host", "")

    @property
    def content_type(self) -> str:
        """Get content type."""
        return self._headers.get("content-type", "")

    @property
    def is_safe(self) -> bool:
        """Check if method is safe."""
        return self._method in SAFE_METHODS

    @property
    def is_idempotent(self) -> bool:
        """Check if method is idempotent."""
        return self._method in IDEMPOTENT_METHODS

    @property
    def is_cacheable(self) -> bool:
        """Check if method is cacheable."""
        return self._method in CACHEABLE_METHODS

    @property
    def scope(self) -> Dict[str, Any]:
        """Get ASGI scope."""
        raise NotImplementedError

    @property
    def stream_id(self) -> int:
        """Get HTTP/3 stream ID."""
        raise SanicException("Stream ID is only a property of a HTTP/3 request")

    async def respond(
        self,
        response: Any = None,
        *,
        status: int = 200,
        headers: Optional[Header] = None,
        content_type: Optional[str] = None,
    ):
        """Start streaming response."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<Request: {self._method} {self.path}>"


__all__ = [
    "Request",
]
