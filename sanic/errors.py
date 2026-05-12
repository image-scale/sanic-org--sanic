class FrameworkError(Exception):
    status_code = 500
    quiet = False

    def __init__(self, message=None, status_code=None, *, quiet=None,
                 context=None, extra=None, headers=None):
        if message is None:
            message = self.__class__.__name__
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if quiet is not None:
            self.quiet = quiet
        self.context = context
        self.extra = extra
        self.headers = headers or {}


class PathNotFound(FrameworkError):
    status_code = 404
    quiet = True


class InvalidMethod(FrameworkError):
    status_code = 405
    quiet = True

    def __init__(self, message=None, method=None, allowed=None, **kwargs):
        super().__init__(message, **kwargs)
        self.method = method
        self.allowed = allowed or []


class BadRequestError(FrameworkError):
    status_code = 400
    quiet = True


class AuthenticationError(FrameworkError):
    status_code = 401
    quiet = True


class PermissionDenied(FrameworkError):
    status_code = 403
    quiet = True


class InternalError(FrameworkError):
    status_code = 500


class PayloadExceeded(FrameworkError):
    status_code = 413
    quiet = True


class RequestExpired(FrameworkError):
    status_code = 408
    quiet = True


class ServiceNotAvailable(FrameworkError):
    status_code = 503
