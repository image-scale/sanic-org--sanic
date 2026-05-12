import asyncio
import json as json_lib
from typing import Optional, Dict, Any


class WebSocketTestClient:
    def __init__(self, sent_messages, received_messages, closed_code=None):
        self.sent = sent_messages
        self.received = received_messages
        self.closed_code = closed_code


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

    def websocket(self, path, client_coro=None, headers=None):
        return self._run(self._ws_request(path, client_coro=client_coro,
                                          headers=headers))

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

    async def _ws_request(self, path, client_coro=None, headers=None):
        if "?" in path:
            path_part, qs = path.split("?", 1)
        else:
            path_part = path
            qs = ""

        req_headers = {}
        if headers:
            req_headers = {k.lower(): v for k, v in headers.items()}

        scope = {
            "type": "websocket",
            "path": path_part,
            "query_string": qs.encode("utf-8"),
            "headers": [
                (k.encode("latin-1"), v.encode("latin-1"))
                for k, v in req_headers.items()
            ],
            "root_path": "",
            "scheme": "ws",
            "server": ("localhost", 80),
            "subprotocols": [],
        }

        client_to_server = asyncio.Queue()
        server_to_client = asyncio.Queue()
        server_sent = []
        close_code = None

        await client_to_server.put({"type": "websocket.connect"})

        async def receive():
            return await client_to_server.get()

        async def send(message):
            nonlocal close_code
            if message["type"] == "websocket.accept":
                pass
            elif message["type"] == "websocket.send":
                server_sent.append(message.get("text") or message.get("bytes"))
                await server_to_client.put(message)
            elif message["type"] == "websocket.close":
                close_code = message.get("code", 1000)
                await server_to_client.put(message)

        client_messages = []

        async def run_client():
            if client_coro is None:
                return

            class ClientWs:
                async def send(self, data):
                    if isinstance(data, bytes):
                        await client_to_server.put(
                            {"type": "websocket.receive", "bytes": data}
                        )
                    else:
                        await client_to_server.put(
                            {"type": "websocket.receive", "text": str(data)}
                        )

                async def recv(self):
                    msg = await server_to_client.get()
                    if msg["type"] == "websocket.close":
                        return None
                    return msg.get("text") or msg.get("bytes")

                receive = recv

                async def close(self):
                    await client_to_server.put({"type": "websocket.disconnect"})

            ws = ClientWs()
            try:
                await client_coro(ws)
            finally:
                await client_to_server.put({"type": "websocket.disconnect"})

        server_task = asyncio.create_task(self.app(scope, receive, send))
        client_task = asyncio.create_task(run_client())

        await asyncio.gather(server_task, client_task, return_exceptions=True)

        return WebSocketTestClient(server_sent, client_messages,
                                   closed_code=close_code)
