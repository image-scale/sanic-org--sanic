import asyncio
import json as json_lib
from typing import Optional, Dict, Any


class TestResponse:
    def __init__(self, status, headers, body, cookies=None):
        self.status = status
        self._headers = headers
        self._body = body
        self._raw_cookies = cookies or []

    @property
    def headers(self):
        return self._headers

    @property
    def body(self):
        return self._body

    @property
    def text(self):
        return self._body.decode("utf-8", errors="replace")

    @property
    def json(self):
        try:
            return json_lib.loads(self._body)
        except Exception:
            return None

    @property
    def content_type(self):
        return self._headers.get("content-type", "")

    @property
    def cookies(self):
        result = {}
        for cookie_str in self._raw_cookies:
            parts = cookie_str.split(";")
            if parts:
                kv = parts[0].strip()
                if "=" in kv:
                    key, _, val = kv.partition("=")
                    result[key.strip()] = val.strip()
        return result

    @property
    def raw_cookies(self):
        return self._raw_cookies


class AppTestClient:
    def __init__(self, app):
        self.app = app

    def _run(self, coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    def get(self, path, headers=None, **kwargs):
        return self._run(self._request("GET", path, headers=headers, **kwargs))

    def post(self, path, headers=None, json=None, data=None, **kwargs):
        return self._run(self._request("POST", path, headers=headers,
                                       json=json, data=data, **kwargs))

    def put(self, path, headers=None, json=None, data=None, **kwargs):
        return self._run(self._request("PUT", path, headers=headers,
                                       json=json, data=data, **kwargs))

    def delete(self, path, headers=None, **kwargs):
        return self._run(self._request("DELETE", path, headers=headers,
                                       **kwargs))

    def patch(self, path, headers=None, json=None, data=None, **kwargs):
        return self._run(self._request("PATCH", path, headers=headers,
                                       json=json, data=data, **kwargs))

    def head(self, path, headers=None, **kwargs):
        return self._run(self._request("HEAD", path, headers=headers,
                                       **kwargs))

    def options(self, path, headers=None, **kwargs):
        return self._run(self._request("OPTIONS", path, headers=headers,
                                       **kwargs))

    async def _request(self, method, path, headers=None, json=None,
                       data=None, **kwargs):
        if "?" in path:
            path_part, qs = path.split("?", 1)
        else:
            path_part = path
            qs = ""

        body = b""
        req_headers = {}
        if headers:
            req_headers = {k.lower(): v for k, v in headers.items()}

        if json is not None:
            body = json_lib.dumps(json).encode("utf-8")
            req_headers.setdefault("content-type", "application/json")
        elif data is not None:
            if isinstance(data, bytes):
                body = data
            elif isinstance(data, str):
                body = data.encode("utf-8")

        scope = {
            "type": "http",
            "method": method,
            "path": path_part,
            "query_string": qs.encode("utf-8"),
            "headers": [
                (k.encode("latin-1"), v.encode("latin-1"))
                for k, v in req_headers.items()
            ],
            "root_path": "",
            "scheme": "http",
            "server": ("localhost", 80),
        }

        response_started = False
        response_status = 500
        response_headers = {}
        response_cookies = []
        response_body = b""

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            nonlocal response_started, response_status, response_headers, response_body
            if message["type"] == "http.response.start":
                response_started = True
                response_status = message["status"]
                for hname, hval in message.get("headers", []):
                    key = hname.decode("latin-1").lower()
                    val = hval.decode("latin-1")
                    if key == "set-cookie":
                        response_cookies.append(val)
                    else:
                        response_headers[key] = val
            elif message["type"] == "http.response.body":
                response_body = message.get("body", b"")

        await self.app(scope, receive, send)

        return TestResponse(response_status, response_headers, response_body,
                            cookies=response_cookies)
