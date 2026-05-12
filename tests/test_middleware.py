import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import make_json, make_text


class TestMiddlewareRegistration:
    def test_register_request_middleware_with_decorator(self, app, client):
        order = []

        @app.middleware("request")
        async def mw(request):
            order.append("mw")

        @app.get("/test")
        async def handler(request):
            return make_text("ok")

        resp = client.get("/test")
        assert resp.status == 200
        assert order == ["mw"]

    def test_register_response_middleware_with_decorator(self, app, client):
        order = []

        @app.middleware("response")
        async def mw(request, response):
            order.append("mw")

        @app.get("/test")
        async def handler(request):
            return make_text("ok")

        resp = client.get("/test")
        assert resp.status == 200
        assert order == ["mw"]

    def test_on_request_shortcut(self, app, client):
        received_methods = []

        @app.on_request
        async def mw(request):
            received_methods.append(request.method)

        @app.get("/test")
        async def handler(request):
            return make_text("ok")

        client.get("/test")
        assert received_methods == ["GET"]

    def test_on_response_shortcut(self, app, client):
        statuses = []

        @app.on_response
        async def mw(request, response):
            statuses.append(response.status)

        @app.get("/test")
        async def handler(request):
            return make_json({"ok": True})

        client.get("/test")
        assert statuses == [200]


class TestMiddlewareBehavior:
    def test_request_mw_receives_request(self, app, client):
        captured = {}

        @app.on_request
        async def mw(request):
            captured["path"] = request.path
            captured["method"] = request.method

        @app.get("/info")
        async def handler(request):
            return make_text("ok")

        client.get("/info")
        assert captured == {"path": "/info", "method": "GET"}

    def test_response_mw_receives_request_and_response(self, app, client):
        captured = {}

        @app.on_response
        async def mw(request, response):
            captured["req_path"] = request.path
            captured["resp_status"] = response.status

        @app.get("/data")
        async def handler(request):
            return make_json({"x": 1}, status=201)

        client.get("/data")
        assert captured == {"req_path": "/data", "resp_status": 201}

    def test_request_mw_short_circuits(self, app, client):
        handler_called = []

        @app.on_request
        async def mw(request):
            return make_text("blocked", status=403)

        @app.get("/secret")
        async def handler(request):
            handler_called.append(True)
            return make_text("ok")

        resp = client.get("/secret")
        assert resp.status == 403
        assert resp.text == "blocked"
        assert handler_called == []

    def test_response_mw_can_replace_response(self, app, client):
        @app.on_response
        async def mw(request, response):
            return make_json({"wrapped": True}, status=200)

        @app.get("/original")
        async def handler(request):
            return make_text("original")

        resp = client.get("/original")
        assert resp.json == {"wrapped": True}

    def test_request_mw_returning_none_continues(self, app, client):
        order = []

        @app.on_request
        async def mw1(request):
            order.append("mw1")
            return None

        @app.on_request
        async def mw2(request):
            order.append("mw2")

        @app.get("/test")
        async def handler(request):
            order.append("handler")
            return make_text("ok")

        client.get("/test")
        assert order == ["mw1", "mw2", "handler"]


class TestMiddlewareOrdering:
    def test_request_mw_runs_in_registration_order(self, app, client):
        order = []

        @app.on_request
        async def mw1(request):
            order.append("first")

        @app.on_request
        async def mw2(request):
            order.append("second")

        @app.on_request
        async def mw3(request):
            order.append("third")

        @app.get("/test")
        async def handler(request):
            return make_text("ok")

        client.get("/test")
        assert order == ["first", "second", "third"]

    def test_response_mw_runs_in_reverse_order(self, app, client):
        order = []

        @app.on_response
        async def mw1(request, response):
            order.append("first_registered")

        @app.on_response
        async def mw2(request, response):
            order.append("second_registered")

        @app.on_response
        async def mw3(request, response):
            order.append("third_registered")

        @app.get("/test")
        async def handler(request):
            return make_text("ok")

        client.get("/test")
        assert order == ["third_registered", "second_registered", "first_registered"]

    def test_priority_controls_request_ordering(self, app, client):
        order = []

        @app.on_request(priority=0)
        async def low_priority(request):
            order.append("low")

        @app.on_request(priority=10)
        async def high_priority(request):
            order.append("high")

        @app.get("/test")
        async def handler(request):
            return make_text("ok")

        client.get("/test")
        assert order == ["high", "low"]


class TestAsyncMiddleware:
    def test_async_request_middleware(self, app, client):
        import asyncio

        marker = []

        @app.on_request
        async def mw(request):
            await asyncio.sleep(0)
            marker.append("async_ran")

        @app.get("/test")
        async def handler(request):
            return make_text("ok")

        client.get("/test")
        assert marker == ["async_ran"]

    def test_async_response_middleware(self, app, client):
        import asyncio

        @app.on_response
        async def mw(request, response):
            await asyncio.sleep(0)
            response.headers["x-async"] = "yes"

        @app.get("/test")
        async def handler(request):
            return make_text("ok")

        resp = client.get("/test")
        assert resp.headers.get("x-async") == "yes"
