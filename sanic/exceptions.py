"""Sanic exceptions."""
from typing import Any, Dict, Optional, Union


class SanicException(Exception):
    """Base Sanic exception class."""

    status_code: int = 500
    quiet: bool = False
    message: str = "Internal Server Error"

    def __init__(
        self,
        message: Optional[Union[str, bytes]] = None,
        status_code: Optional[int] = None,
        *,
        quiet: Optional[bool] = None,
        context: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        if message is None and not hasattr(self.__class__, "message"):
            message = "Internal Server Error"

        if isinstance(message, bytes):
            message = message.decode("utf-8")

        if message is not None:
            self.message = message
        elif hasattr(self.__class__, "message"):
            # message = self.__class__.message
            pass
        else:
            self.message = "Internal Server Error"

        if status_code is not None:
            self.status_code = status_code

        if quiet is not None:
            self.quiet = quiet

        self.context = context
        self.extra = extra or {}
        self.headers = headers or {}

        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class BadRequest(SanicException):
    """HTTP 400 Bad Request."""

    status_code = 400
    message = "Bad Request"


# Alias for backwards compatibility
InvalidUsage = BadRequest


class Unauthorized(SanicException):
    """HTTP 401 Unauthorized."""

    status_code = 401
    message = "Unauthorized"

    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        *,
        scheme: Optional[str] = None,
        realm: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, status_code, **kwargs)
        self.scheme = scheme
        self.realm = realm
        self.challenge_kwargs = kwargs


class Forbidden(SanicException):
    """HTTP 403 Forbidden."""

    status_code = 403
    message = "Forbidden"


class NotFound(SanicException):
    """HTTP 404 Not Found."""

    status_code = 404
    message = "Not Found"


class MethodNotAllowed(SanicException):
    """HTTP 405 Method Not Allowed."""

    status_code = 405
    message = "Method Not Allowed"

    def __init__(
        self,
        message: Optional[str] = None,
        method: Optional[str] = None,
        allowed_methods: Optional[Any] = None,
        *,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, status_code, **kwargs)
        self.method = method
        self.allowed_methods = allowed_methods


# Alias for backwards compatibility
MethodNotSupported = MethodNotAllowed


class RequestTimeout(SanicException):
    """HTTP 408 Request Timeout."""

    status_code = 408
    message = "Request Timeout"


class RangeNotSatisfiable(SanicException):
    """HTTP 416 Range Not Satisfiable."""

    status_code = 416
    message = "Range Not Satisfiable"


# Alias for backwards compatibility
ContentRangeError = RangeNotSatisfiable


class ExpectationFailed(SanicException):
    """HTTP 417 Expectation Failed."""

    status_code = 417
    message = "Expectation Failed"


# Alias for backwards compatibility
HeaderExpectationFailed = ExpectationFailed


class ServerError(SanicException):
    """HTTP 500 Internal Server Error."""

    status_code = 500
    message = "Internal Server Error"


class ServiceUnavailable(SanicException):
    """HTTP 503 Service Unavailable."""

    status_code = 503
    message = "Service Unavailable"


class LoadFileException(SanicException):
    """Exception when loading file fails."""

    pass


class PayloadTooLarge(SanicException):
    """HTTP 413 Payload Too Large."""

    status_code = 413
    message = "Payload Too Large"


class InvalidSignal(SanicException):
    """Invalid signal exception."""

    pass


class BadURL(SanicException):
    """Bad URL exception."""

    pass


class PyFileError(Exception):
    """Python file error exception."""

    def __init__(self, file_path: str, exc: Exception):
        self.file_path = file_path
        self.exc = exc
        super().__init__(f"Error loading {file_path}: {exc}")


class URLBuildError(SanicException):
    """URL build error exception."""

    pass


class WebsocketClosed(SanicException):
    """Websocket closed exception."""

    pass


class InvalidHeader(SanicException):
    """Invalid header exception."""

    status_code = 400


class FileNotFound(NotFound):
    """File not found exception."""

    pass


class ServerKilled(SanicException):
    """Server killed exception."""

    pass


class Redirect(SanicException):
    """Redirect exception - used for flow control in some handlers."""

    status_code = 302

    def __init__(
        self,
        url: str,
        status: int = 302,
        **kwargs,
    ):
        self.url = url
        super().__init__(status_code=status, **kwargs)


__all__ = [
    "SanicException",
    "BadRequest",
    "InvalidUsage",
    "Unauthorized",
    "Forbidden",
    "NotFound",
    "MethodNotAllowed",
    "MethodNotSupported",
    "RequestTimeout",
    "RangeNotSatisfiable",
    "ContentRangeError",
    "ExpectationFailed",
    "HeaderExpectationFailed",
    "ServerError",
    "ServiceUnavailable",
    "LoadFileException",
    "PayloadTooLarge",
    "InvalidSignal",
    "BadURL",
    "PyFileError",
    "URLBuildError",
    "WebsocketClosed",
    "InvalidHeader",
    "FileNotFound",
    "ServerKilled",
    "Redirect",
]
