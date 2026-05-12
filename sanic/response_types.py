import json as json_lib
from typing import Any, Optional, Dict

from .cookie_utils import ResponseCookieJar


class ServerResponse:
    def __init__(self, body=None, status=200, headers=None,
                 content_type=None):
        if isinstance(body, str):
            self._body = body.encode("utf-8")
        elif isinstance(body, bytes):
            self._body = body
        elif body is None:
            self._body = b""
        else:
            self._body = str(body).encode("utf-8")
        self.status = status
        self._headers = {}
        if headers:
            for k, v in headers.items():
                self._headers[k.lower()] = v
        if content_type:
            self._headers["content-type"] = content_type
        self._cookie_jar = ResponseCookieJar()

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        if isinstance(value, str):
            self._body = value.encode("utf-8")
        elif isinstance(value, bytes):
            self._body = value
        elif value is None:
            self._body = b""
        else:
            self._body = str(value).encode("utf-8")

    @property
    def headers(self):
        return self._headers

    @property
    def content_type(self):
        return self._headers.get("content-type", "")

    @content_type.setter
    def content_type(self, value):
        self._headers["content-type"] = value

    @property
    def json(self):
        try:
            return json_lib.loads(self._body)
        except Exception:
            return None

    @property
    def cookie_jar(self):
        return self._cookie_jar

    def add_cookie(self, key, value, **kwargs):
        return self._cookie_jar.add(key, value, **kwargs)

    def delete_cookie(self, key, **kwargs):
        return self._cookie_jar.delete(key, **kwargs)


class JsonPayload(ServerResponse):
    def __init__(self, body=None, status=200, headers=None,
                 content_type="application/json", dumps=None, **kwargs):
        self._dumps = dumps or json_lib.dumps
        self._raw_body = body
        encoded = self._dumps(body, **kwargs) if body is not None else ""
        super().__init__(
            body=encoded,
            status=status,
            headers=headers,
            content_type=content_type,
        )

    @property
    def raw_body(self):
        return self._raw_body

    @raw_body.setter
    def raw_body(self, value):
        self._raw_body = value
        self.body = self._dumps(value)


def make_json(body, status=200, headers=None,
              content_type="application/json", dumps=None, **kwargs):
    return JsonPayload(body, status=status, headers=headers,
                       content_type=content_type, dumps=dumps, **kwargs)


def make_text(body, status=200, headers=None,
              content_type="text/plain; charset=utf-8"):
    return ServerResponse(body=body, status=status, headers=headers,
                          content_type=content_type)


def make_html(body, status=200, headers=None):
    return ServerResponse(body=body, status=status, headers=headers,
                          content_type="text/html; charset=utf-8")


def make_raw(body, status=200, headers=None,
             content_type="application/octet-stream"):
    return ServerResponse(body=body, status=status, headers=headers,
                          content_type=content_type)


def make_redirect(to, headers=None, status=302,
                  content_type="text/html; charset=utf-8"):
    h = dict(headers) if headers else {}
    h["location"] = to
    return ServerResponse(body=b"", status=status, headers=h,
                          content_type=content_type)


def make_empty(status=204, headers=None):
    return ServerResponse(body=b"", status=status, headers=headers)
