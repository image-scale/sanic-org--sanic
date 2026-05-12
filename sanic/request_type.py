import json as json_lib
from urllib.parse import parse_qs

from .cookie_utils import parse_request_cookies


class RequestData:
    __slots__ = (
        "_app", "_method", "_path", "_headers", "_body", "_version",
        "_query_string", "_parsed_json", "_parsed_args", "_parsed_form",
        "_match_info", "_route", "_raw_url", "_content_type",
        "_transport_info", "_parsed_cookies",
    )

    def __init__(self, method, path, headers=None, body=b"", version="1.1",
                 query_string="", app=None):
        self._method = method.upper()
        self._path = path
        self._headers = headers or {}
        self._body = body if isinstance(body, bytes) else body.encode("utf-8")
        self._version = version
        self._query_string = query_string
        self._parsed_json = None
        self._parsed_args = None
        self._parsed_form = None
        self._match_info = {}
        self._route = None
        self._app = app
        self._raw_url = path
        self._content_type = None
        self._transport_info = None
        self._parsed_cookies = None

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path

    @property
    def url(self):
        if self._query_string:
            return f"{self._path}?{self._query_string}"
        return self._path

    @property
    def headers(self):
        return self._headers

    @property
    def body(self):
        return self._body

    @property
    def version(self):
        return self._version

    @property
    def query_string(self):
        return self._query_string

    @property
    def content_type(self):
        if self._content_type is None:
            self._content_type = self._headers.get("content-type", "")
        return self._content_type

    @property
    def json(self):
        if self._parsed_json is None and self._body:
            try:
                self._parsed_json = json_lib.loads(self._body)
            except (json_lib.JSONDecodeError, UnicodeDecodeError):
                self._parsed_json = None
        return self._parsed_json

    @property
    def args(self):
        if self._parsed_args is None:
            self._parsed_args = parse_qs(self._query_string, keep_blank_values=True)
        return self._parsed_args

    @property
    def match_info(self):
        return self._match_info

    @match_info.setter
    def match_info(self, value):
        self._match_info = value

    @property
    def route(self):
        return self._route

    @route.setter
    def route(self, value):
        self._route = value

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value):
        self._app = value

    @property
    def ip(self):
        return ""

    @property
    def cookies(self):
        if self._parsed_cookies is None:
            raw = self._headers.get("cookie", "")
            self._parsed_cookies = parse_request_cookies(raw)
        return self._parsed_cookies

    def get_args(self, key, default=None):
        vals = self.args.get(key)
        if vals:
            return vals[0]
        return default
