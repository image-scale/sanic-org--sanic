import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import (
    make_json, make_text, make_html, make_raw, make_redirect, make_empty,
)


class TestAppCreation:
    def test_create_app_with_name(self):
        app = Sanic("my_app")
        assert app.name == "my_app"
        Sanic._registry.pop("my_app", None)

    def test_app_registry(self):
        app = Sanic("registry_test")
        found = Sanic.get_app("registry_test")
        assert found is app
        Sanic._registry.pop("registry_test", None)


class TestRouteRegistration:
    def test_get_route(self, app, client):
        @app.get("/hello")
        async def handler(request):
            return make_text("hello world")

        resp = client.get("/hello")
        assert resp.status == 200
        assert resp.text == "hello world"

    def test_post_route(self, app, client):
        @app.post("/items")
        async def handler(request):
            return make_json({"created": True}, status=201)

        resp = client.post("/items")
        assert resp.status == 201
        assert resp.json == {"created": True}

    def test_put_route(self, app, client):
        @app.put("/items/<item_id:int>")
        async def handler(request, item_id):
            return make_json({"updated": item_id})

        resp = client.put("/items/42")
        assert resp.status == 200
        assert resp.json == {"updated": 42}

    def test_delete_route(self, app, client):
        @app.delete("/items/<item_id:int>")
        async def handler(request, item_id):
            return make_empty()

        resp = client.delete("/items/7")
        assert resp.status == 204

    def test_patch_route(self, app, client):
        @app.patch("/items/<item_id:int>")
        async def handler(request, item_id):
            return make_json({"patched": item_id})

        resp = client.patch("/items/5")
        assert resp.status == 200
        assert resp.json == {"patched": 5}

    def test_head_route(self, app, client):
        @app.head("/ping")
        async def handler(request):
            return make_empty(status=200)

        resp = client.head("/ping")
        assert resp.status == 200

    def test_options_route(self, app, client):
        @app.options("/resource")
        async def handler(request):
            return make_text("", headers={"allow": "GET, POST"})

        resp = client.options("/resource")
        assert resp.status == 200
        assert resp.headers.get("allow") == "GET, POST"

    def test_multi_method_route(self, app, client):
        @app.route("/multi", methods=["GET", "POST"])
        async def handler(request):
            return make_json({"method": request.method})

        resp_get = client.get("/multi")
        assert resp_get.json == {"method": "GET"}

        resp_post = client.post("/multi")
        assert resp_post.json == {"method": "POST"}


class TestPathParameters:
    def test_string_param(self, app, client):
        @app.get("/users/<username>")
        async def handler(request, username):
            return make_json({"user": username})

        resp = client.get("/users/alice")
        assert resp.json == {"user": "alice"}

    def test_int_param(self, app, client):
        @app.get("/items/<item_id:int>")
        async def handler(request, item_id):
            return make_json({"id": item_id, "type": type(item_id).__name__})

        resp = client.get("/items/123")
        assert resp.json["id"] == 123
        assert resp.json["type"] == "int"

    def test_float_param(self, app, client):
        @app.get("/price/<value:float>")
        async def handler(request, value):
            return make_json({"price": value, "type": type(value).__name__})

        resp = client.get("/price/19.99")
        assert resp.json["price"] == 19.99
        assert resp.json["type"] == "float"

    def test_default_string_type(self, app, client):
        @app.get("/tag/<name>")
        async def handler(request, name):
            return make_json({"name": name, "type": type(name).__name__})

        resp = client.get("/tag/python")
        assert resp.json["name"] == "python"
        assert resp.json["type"] == "str"

    def test_multiple_params(self, app, client):
        @app.get("/org/<org>/repo/<repo>")
        async def handler(request, org, repo):
            return make_json({"org": org, "repo": repo})

        resp = client.get("/org/acme/repo/widget")
        assert resp.json == {"org": "acme", "repo": "widget"}


class TestRequestObject:
    def test_request_method(self, app, client):
        @app.get("/method")
        async def handler(request):
            return make_text(request.method)

        resp = client.get("/method")
        assert resp.text == "GET"

    def test_request_path(self, app, client):
        @app.get("/my/path")
        async def handler(request):
            return make_text(request.path)

        resp = client.get("/my/path")
        assert resp.text == "/my/path"

    def test_request_headers(self, app, client):
        @app.get("/echo-header")
        async def handler(request):
            val = request.headers.get("x-custom", "missing")
            return make_text(val)

        resp = client.get("/echo-header", headers={"X-Custom": "hello123"})
        assert resp.text == "hello123"

    def test_request_query_args(self, app, client):
        @app.get("/search")
        async def handler(request):
            q = request.args.get("q", [""])[0]
            page = request.args.get("page", ["1"])[0]
            return make_json({"q": q, "page": page})

        resp = client.get("/search?q=python&page=2")
        assert resp.json == {"q": "python", "page": "2"}

    def test_request_json_body(self, app, client):
        @app.post("/echo")
        async def handler(request):
            return make_json(request.json)

        resp = client.post("/echo", json={"key": "value"})
        assert resp.json == {"key": "value"}

    def test_request_body_bytes(self, app, client):
        @app.post("/raw-body")
        async def handler(request):
            return make_text(f"got {len(request.body)} bytes")

        resp = client.post("/raw-body", data=b"hello bytes")
        assert resp.text == "got 11 bytes"


class TestResponseHelpers:
    def test_json_response(self, app, client):
        @app.get("/json")
        async def handler(request):
            return make_json({"msg": "ok"})

        resp = client.get("/json")
        assert resp.status == 200
        assert resp.json == {"msg": "ok"}
        assert "application/json" in resp.content_type

    def test_text_response(self, app, client):
        @app.get("/text")
        async def handler(request):
            return make_text("plain text")

        resp = client.get("/text")
        assert resp.status == 200
        assert resp.text == "plain text"
        assert "text/plain" in resp.content_type

    def test_html_response(self, app, client):
        @app.get("/html")
        async def handler(request):
            return make_html("<h1>Hello</h1>")

        resp = client.get("/html")
        assert resp.status == 200
        assert resp.text == "<h1>Hello</h1>"
        assert "text/html" in resp.content_type

    def test_raw_response(self, app, client):
        @app.get("/raw")
        async def handler(request):
            return make_raw(b"\x00\x01\x02")

        resp = client.get("/raw")
        assert resp.status == 200
        assert resp.body == b"\x00\x01\x02"
        assert "application/octet-stream" in resp.content_type

    def test_redirect_response(self, app, client):
        @app.get("/old")
        async def handler(request):
            return make_redirect("/new")

        resp = client.get("/old")
        assert resp.status == 302
        assert resp.headers.get("location") == "/new"

    def test_empty_response(self, app, client):
        @app.delete("/resource")
        async def handler(request):
            return make_empty()

        resp = client.delete("/resource")
        assert resp.status == 204
        assert resp.body == b""

    def test_custom_status_code(self, app, client):
        @app.post("/create")
        async def handler(request):
            return make_json({"id": 1}, status=201)

        resp = client.post("/create")
        assert resp.status == 201

    def test_custom_headers(self, app, client):
        @app.get("/custom-headers")
        async def handler(request):
            return make_json(
                {"ok": True},
                headers={"x-request-id": "abc123"}
            )

        resp = client.get("/custom-headers")
        assert resp.headers.get("x-request-id") == "abc123"


class TestErrorHandling:
    def test_not_found(self, app, client):
        resp = client.get("/nonexistent")
        assert resp.status == 404

    def test_method_not_allowed(self, app, client):
        @app.get("/only-get")
        async def handler(request):
            return make_text("ok")

        resp = client.post("/only-get")
        assert resp.status == 405

    def test_method_not_allowed_has_allow_header(self, app, client):
        @app.get("/only-get-2")
        async def handler(request):
            return make_text("ok")

        resp = client.post("/only-get-2")
        assert resp.status == 405
        assert "GET" in resp.headers.get("allow", "")


class TestTestClient:
    def test_client_get(self, app, client):
        @app.get("/test")
        async def handler(request):
            return make_text("works")

        resp = client.get("/test")
        assert resp.status == 200
        assert resp.text == "works"

    def test_client_post_json(self, app, client):
        @app.post("/test")
        async def handler(request):
            return make_json(request.json)

        resp = client.post("/test", json={"a": 1})
        assert resp.json == {"a": 1}

    def test_client_returns_headers(self, app, client):
        @app.get("/h")
        async def handler(request):
            return make_text("ok", headers={"x-foo": "bar"})

        resp = client.get("/h")
        assert resp.headers["x-foo"] == "bar"

    def test_client_delete(self, app, client):
        @app.delete("/del")
        async def handler(request):
            return make_empty()

        resp = client.delete("/del")
        assert resp.status == 204

    def test_client_patch(self, app, client):
        @app.patch("/p")
        async def handler(request):
            return make_json({"patched": True})

        resp = client.patch("/p", json={"field": "val"})
        assert resp.json == {"patched": True}
