import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import make_json, make_text, make_empty
from sanic.method_views import MethodBasedView


class TestBasicMethodView:
    def test_get_method(self, app, client):
        class ItemView(MethodBasedView):
            async def get(self, request):
                return make_json({"items": [1, 2, 3]})

        ItemView.attach_to(app, "/items")
        resp = client.get("/items")
        assert resp.status == 200
        assert resp.json == {"items": [1, 2, 3]}

    def test_post_method(self, app, client):
        class ItemView(MethodBasedView):
            async def post(self, request):
                return make_json({"created": True}, status=201)

        ItemView.attach_to(app, "/items")
        resp = client.post("/items")
        assert resp.status == 201
        assert resp.json == {"created": True}

    def test_put_method(self, app, client):
        class ItemView(MethodBasedView):
            async def put(self, request, item_id):
                return make_json({"updated": item_id})

        ItemView.attach_to(app, "/items/<item_id:int>")
        resp = client.put("/items/42")
        assert resp.json == {"updated": 42}

    def test_patch_method(self, app, client):
        class ItemView(MethodBasedView):
            async def patch(self, request):
                return make_json({"patched": True})

        ItemView.attach_to(app, "/items")
        resp = client.patch("/items")
        assert resp.json == {"patched": True}

    def test_delete_method(self, app, client):
        class ItemView(MethodBasedView):
            async def delete(self, request):
                return make_empty()

        ItemView.attach_to(app, "/items")
        resp = client.delete("/items")
        assert resp.status == 204


class TestMultipleMethodsOnView:
    def test_dispatches_to_correct_method(self, app, client):
        class ResourceView(MethodBasedView):
            async def get(self, request):
                return make_json({"method": "GET"})

            async def post(self, request):
                return make_json({"method": "POST"})

            async def delete(self, request):
                return make_json({"method": "DELETE"})

        ResourceView.attach_to(app, "/resource")
        assert client.get("/resource").json == {"method": "GET"}
        assert client.post("/resource").json == {"method": "POST"}
        assert client.delete("/resource").json == {"method": "DELETE"}


class TestViewDecorators:
    def test_decorators_applied_to_all_methods(self, app, client):
        call_log = []

        def log_decorator(f):
            async def wrapper(request, **kwargs):
                call_log.append("decorated")
                return await f(request, **kwargs)
            return wrapper

        class DecoratedView(MethodBasedView):
            decorators = [log_decorator]

            async def get(self, request):
                return make_text("hello")

        DecoratedView.attach_to(app, "/decorated")
        resp = client.get("/decorated")
        assert resp.status == 200
        assert resp.text == "hello"
        assert call_log == ["decorated"]


class TestViewAutoDetectMethods:
    def test_auto_detect_supported_methods(self):
        class MyView(MethodBasedView):
            async def get(self, request):
                pass

            async def post(self, request):
                pass

        methods = MyView._get_supported_methods()
        assert "GET" in methods
        assert "POST" in methods
        assert "DELETE" not in methods

    def test_unsupported_method_returns_405(self, app, client):
        class GetOnlyView(MethodBasedView):
            async def get(self, request):
                return make_text("ok")

        GetOnlyView.attach_to(app, "/get-only")
        resp = client.post("/get-only")
        assert resp.status == 405


class TestViewWithPathParams:
    def test_path_params_passed_to_method(self, app, client):
        class UserView(MethodBasedView):
            async def get(self, request, user_id):
                return make_json({"user_id": user_id})

        UserView.attach_to(app, "/users/<user_id:int>")
        resp = client.get("/users/99")
        assert resp.json == {"user_id": 99}


class TestViewAsHandler:
    def test_as_handler_creates_callable(self, app, client):
        class SimpleView(MethodBasedView):
            async def get(self, request):
                return make_text("from handler")

        handler = SimpleView.as_handler()
        app.route("/simple", methods=["GET"])(handler)
        resp = client.get("/simple")
        assert resp.text == "from handler"
