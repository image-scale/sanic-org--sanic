import asyncio
import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient, WebSocketTestClient
from sanic.websocket import WebSocketConnection


class TestWebSocketConnection:
    def test_connection_init(self):
        async def send(msg): pass
        async def receive(): pass
        ws = WebSocketConnection(send, receive)
        assert not ws.closed
        assert ws._accepted is False


class TestWebSocketRouteRegistration:
    def test_websocket_decorator(self):
        app = Sanic("ws_reg_1")

        @app.websocket("/ws")
        async def handler(request, ws):
            pass

        route = app.router.find_by_name("handler")
        assert route is not None
        assert route.uri == "/ws"
        Sanic._registry.pop("ws_reg_1", None)

    def test_websocket_with_custom_name(self):
        app = Sanic("ws_reg_2")

        @app.websocket("/ws", name="my_ws")
        async def handler(request, ws):
            pass

        route = app.router.find_by_name("my_ws")
        assert route is not None
        Sanic._registry.pop("ws_reg_2", None)


class TestWebSocketEcho:
    def test_echo(self):
        app = Sanic("ws_echo_1")

        @app.websocket("/echo")
        async def echo(request, ws):
            data = await ws.recv()
            if data is not None:
                await ws.send(f"echo: {data}")

        client = AppTestClient(app)

        async def client_fn(ws):
            await ws.send("hello")
            result = await ws.recv()
            assert result == "echo: hello"

        result = client.websocket("/echo", client_coro=client_fn)
        assert "echo: hello" in result.sent
        Sanic._registry.pop("ws_echo_1", None)


class TestWebSocketMultipleMessages:
    def test_multiple_messages(self):
        app = Sanic("ws_multi_1")

        @app.websocket("/chat")
        async def chat(request, ws):
            for i in range(3):
                data = await ws.recv()
                if data is None:
                    break
                await ws.send(f"msg{i}: {data}")

        client = AppTestClient(app)

        async def client_fn(ws):
            for i in range(3):
                await ws.send(f"hello{i}")
                resp = await ws.recv()

        result = client.websocket("/chat", client_coro=client_fn)
        assert len(result.sent) == 3
        assert "msg0: hello0" in result.sent
        assert "msg1: hello1" in result.sent
        assert "msg2: hello2" in result.sent
        Sanic._registry.pop("ws_multi_1", None)


class TestWebSocketBinary:
    def test_binary_message(self):
        app = Sanic("ws_bin_1")

        @app.websocket("/binary")
        async def handler(request, ws):
            data = await ws.recv()
            if data is not None:
                await ws.send(data)

        client = AppTestClient(app)

        async def client_fn(ws):
            await ws.send(b"\x00\x01\x02")
            result = await ws.recv()
            assert result == b"\x00\x01\x02"

        result = client.websocket("/binary", client_coro=client_fn)
        assert b"\x00\x01\x02" in result.sent
        Sanic._registry.pop("ws_bin_1", None)


class TestWebSocketIterator:
    def test_async_for_iteration(self):
        app = Sanic("ws_iter_1")
        received = []

        @app.websocket("/iter")
        async def handler(request, ws):
            async for msg in ws:
                received.append(msg)
                await ws.send(f"got: {msg}")

        client = AppTestClient(app)

        async def client_fn(ws):
            await ws.send("a")
            await ws.recv()
            await ws.send("b")
            await ws.recv()

        result = client.websocket("/iter", client_coro=client_fn)
        assert received == ["a", "b"]
        assert len(result.sent) == 2
        Sanic._registry.pop("ws_iter_1", None)


class TestWebSocketWithPathParams:
    def test_path_params(self):
        app = Sanic("ws_params_1")

        @app.websocket("/rooms/<room_id:int>")
        async def handler(request, ws, room_id):
            await ws.send(f"room: {room_id}")

        client = AppTestClient(app)

        async def client_fn(ws):
            result = await ws.recv()
            assert result == "room: 42"

        result = client.websocket("/rooms/42", client_coro=client_fn)
        assert "room: 42" in result.sent
        Sanic._registry.pop("ws_params_1", None)


class TestWebSocketClose:
    def test_server_closes(self):
        app = Sanic("ws_close_1")

        @app.websocket("/close")
        async def handler(request, ws):
            await ws.send("bye")
            await ws.close(code=1000)

        client = AppTestClient(app)

        async def client_fn(ws):
            msg = await ws.recv()
            assert msg == "bye"

        result = client.websocket("/close", client_coro=client_fn)
        assert result.closed_code == 1000
        Sanic._registry.pop("ws_close_1", None)


class TestWebSocketRequestAccess:
    def test_request_headers(self):
        app = Sanic("ws_req_1")

        @app.websocket("/headers")
        async def handler(request, ws):
            token = request.headers.get("x-token", "none")
            await ws.send(f"token: {token}")

        client = AppTestClient(app)

        async def client_fn(ws):
            result = await ws.recv()
            assert result == "token: secret123"

        result = client.websocket("/headers", client_coro=client_fn,
                                  headers={"X-Token": "secret123"})
        assert "token: secret123" in result.sent
        Sanic._registry.pop("ws_req_1", None)

    def test_request_query_string(self):
        app = Sanic("ws_req_2")

        @app.websocket("/query")
        async def handler(request, ws):
            name_list = request.args.get("name", ["world"])
            name = name_list[0] if isinstance(name_list, list) else name_list
            await ws.send(f"hello {name}")

        client = AppTestClient(app)

        async def client_fn(ws):
            result = await ws.recv()
            assert result == "hello sanic"

        result = client.websocket("/query?name=sanic", client_coro=client_fn)
        assert "hello sanic" in result.sent
        Sanic._registry.pop("ws_req_2", None)


class TestWebSocketNotFound:
    def test_nonexistent_route(self):
        app = Sanic("ws_404_1")
        client = AppTestClient(app)

        async def client_fn(ws):
            pass

        result = client.websocket("/nonexistent", client_coro=client_fn)
        assert result.closed_code == 4004
        Sanic._registry.pop("ws_404_1", None)
