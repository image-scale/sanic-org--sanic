import enum


class HttpMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

    def __str__(self):
        return self.value


ALL_HTTP_METHODS = tuple(m.value for m in HttpMethod)
SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
IDEMPOTENT_METHODS = ("GET", "HEAD", "PUT", "DELETE", "OPTIONS")
