import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import make_json, make_text
from sanic.blueprints import Blueprint, group


class TestRouteVersioning:
    def test_integer_version(self):
        app = Sanic("ver_1")

        @app.get("/users", version=1)
        async def handler(request):
            return make_json({"version": 1})

        client = AppTestClient(app)
        resp = client.get("/v1/users")
        assert resp.status == 200
        assert resp.json == {"version": 1}
        Sanic._registry.pop("ver_1", None)

    def test_version_2(self):
        app = Sanic("ver_2")

        @app.get("/users", version=2)
        async def handler(request):
            return make_json({"version": 2})

        client = AppTestClient(app)
        resp = client.get("/v2/users")
        assert resp.status == 200
        assert resp.json == {"version": 2}
        Sanic._registry.pop("ver_2", None)

    def test_float_version(self):
        app = Sanic("ver_3")

        @app.get("/items", version=1.5)
        async def handler(request):
            return make_json({"version": 1.5})

        client = AppTestClient(app)
        resp = client.get("/v1.5/items")
        assert resp.status == 200
        assert resp.json == {"version": 1.5}
        Sanic._registry.pop("ver_3", None)

    def test_string_version(self):
        app = Sanic("ver_4")

        @app.get("/data", version="beta")
        async def handler(request):
            return make_text("beta")

        client = AppTestClient(app)
        resp = client.get("/vbeta/data")
        assert resp.status == 200
        assert resp.text == "beta"
        Sanic._registry.pop("ver_4", None)

    def test_custom_version_prefix(self):
        app = Sanic("ver_5")

        @app.get("/items", version=1, version_prefix="/api/v")
        async def handler(request):
            return make_json({"prefix": "custom"})

        client = AppTestClient(app)
        resp = client.get("/api/v1/items")
        assert resp.status == 200
        assert resp.json == {"prefix": "custom"}
        Sanic._registry.pop("ver_5", None)

    def test_no_version(self):
        app = Sanic("ver_6")

        @app.get("/health")
        async def handler(request):
            return make_text("ok")

        client = AppTestClient(app)
        resp = client.get("/health")
        assert resp.status == 200
        assert resp.text == "ok"
        Sanic._registry.pop("ver_6", None)

    def test_multiple_versions_same_path(self):
        app = Sanic("ver_7")

        @app.get("/users", version=1, name="users_v1")
        async def handler_v1(request):
            return make_json({"version": 1, "data": "old"})

        @app.get("/users", version=2, name="users_v2")
        async def handler_v2(request):
            return make_json({"version": 2, "data": "new"})

        client = AppTestClient(app)
        resp1 = client.get("/v1/users")
        assert resp1.status == 200
        assert resp1.json["version"] == 1

        resp2 = client.get("/v2/users")
        assert resp2.status == 200
        assert resp2.json["version"] == 2
        Sanic._registry.pop("ver_7", None)


class TestVersionedHTTPMethods:
    def test_post_versioned(self):
        app = Sanic("ver_m_1")

        @app.post("/items", version=1)
        async def handler(request):
            return make_json({"created": True}, status=201)

        client = AppTestClient(app)
        resp = client.post("/v1/items", json={"name": "thing"})
        assert resp.status == 201
        Sanic._registry.pop("ver_m_1", None)

    def test_put_versioned(self):
        app = Sanic("ver_m_2")

        @app.put("/items/<item_id:int>", version=1)
        async def handler(request, item_id):
            return make_json({"id": item_id, "updated": True})

        client = AppTestClient(app)
        resp = client.put("/v1/items/5", json={"name": "updated"})
        assert resp.status == 200
        assert resp.json["id"] == 5
        Sanic._registry.pop("ver_m_2", None)

    def test_delete_versioned(self):
        app = Sanic("ver_m_3")

        @app.delete("/items/<item_id:int>", version=2)
        async def handler(request, item_id):
            return make_json({"deleted": item_id})

        client = AppTestClient(app)
        resp = client.delete("/v2/items/3")
        assert resp.status == 200
        assert resp.json["deleted"] == 3
        Sanic._registry.pop("ver_m_3", None)

    def test_patch_versioned(self):
        app = Sanic("ver_m_4")

        @app.patch("/items/<item_id:int>", version=1)
        async def handler(request, item_id):
            return make_json({"patched": item_id})

        client = AppTestClient(app)
        resp = client.patch("/v1/items/7", json={"field": "val"})
        assert resp.status == 200
        Sanic._registry.pop("ver_m_4", None)


class TestBlueprintVersioning:
    def test_blueprint_level_version(self):
        app = Sanic("bp_ver_1")
        bp = Blueprint("api", url_prefix="/api", version=1)

        @bp.get("/users")
        async def handler(request):
            return make_json({"bp_version": True})

        app.blueprint(bp)
        client = AppTestClient(app)
        resp = client.get("/v1/api/users")
        assert resp.status == 200
        assert resp.json["bp_version"] is True
        Sanic._registry.pop("bp_ver_1", None)

    def test_route_version_overrides_blueprint(self):
        app = Sanic("bp_ver_2")
        bp = Blueprint("api", url_prefix="/api", version=1)

        @bp.get("/items", version=2)
        async def handler(request):
            return make_json({"route_version": 2})

        app.blueprint(bp)
        client = AppTestClient(app)
        resp = client.get("/v2/api/items")
        assert resp.status == 200
        assert resp.json["route_version"] == 2
        Sanic._registry.pop("bp_ver_2", None)

    def test_blueprint_custom_version_prefix(self):
        app = Sanic("bp_ver_3")
        bp = Blueprint("api", url_prefix="/api", version=3,
                       version_prefix="/version-")

        @bp.get("/data")
        async def handler(request):
            return make_text("v3 data")

        app.blueprint(bp)
        client = AppTestClient(app)
        resp = client.get("/version-3/api/data")
        assert resp.status == 200
        assert resp.text == "v3 data"
        Sanic._registry.pop("bp_ver_3", None)


class TestVersionedUrlFor:
    def test_url_for_versioned_route(self):
        app = Sanic("url_ver_1")

        @app.get("/users/<user_id:int>", version=1, name="user_v1")
        async def handler(request, user_id):
            return make_json({"id": user_id})

        url = app.url_for("user_v1", user_id=42)
        assert url == "/v1/users/42"
        Sanic._registry.pop("url_ver_1", None)

    def test_url_for_custom_prefix(self):
        app = Sanic("url_ver_2")

        @app.get("/items", version=2, version_prefix="/api/v",
                 name="items_v2")
        async def handler(request):
            return make_json([])

        url = app.url_for("items_v2")
        assert url == "/api/v2/items"
        Sanic._registry.pop("url_ver_2", None)


class TestVersionedRouteNotFound:
    def test_unversioned_path_404(self):
        app = Sanic("ver_404_1")

        @app.get("/users", version=1)
        async def handler(request):
            return make_json([])

        client = AppTestClient(app)
        resp = client.get("/users")
        assert resp.status == 404
        Sanic._registry.pop("ver_404_1", None)

    def test_wrong_version_404(self):
        app = Sanic("ver_404_2")

        @app.get("/users", version=1)
        async def handler(request):
            return make_json([])

        client = AppTestClient(app)
        resp = client.get("/v2/users")
        assert resp.status == 404
        Sanic._registry.pop("ver_404_2", None)
