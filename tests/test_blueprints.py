import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import make_json, make_text, make_empty
from sanic.blueprints import Blueprint, BlueprintGroup, group as blueprint_group
from sanic.errors import FrameworkError


class TestBlueprintCreation:
    def test_create_blueprint_with_prefix(self, app, client):
        bp = Blueprint("users", url_prefix="/users")

        @bp.get("/list")
        async def list_users(request):
            return make_json({"users": []})

        app.blueprint(bp)
        resp = client.get("/users/list")
        assert resp.status == 200
        assert resp.json == {"users": []}

    def test_blueprint_without_prefix(self, app, client):
        bp = Blueprint("home")

        @bp.get("/welcome")
        async def welcome(request):
            return make_text("welcome")

        app.blueprint(bp)
        resp = client.get("/welcome")
        assert resp.status == 200
        assert resp.text == "welcome"


class TestBlueprintRouteDecorators:
    def test_blueprint_get(self, app, client):
        bp = Blueprint("api", url_prefix="/api")

        @bp.get("/data")
        async def get_data(request):
            return make_json({"data": "value"})

        app.blueprint(bp)
        resp = client.get("/api/data")
        assert resp.json == {"data": "value"}

    def test_blueprint_post(self, app, client):
        bp = Blueprint("api", url_prefix="/api")

        @bp.post("/items")
        async def create_item(request):
            return make_json({"created": True}, status=201)

        app.blueprint(bp)
        resp = client.post("/api/items")
        assert resp.status == 201

    def test_blueprint_put(self, app, client):
        bp = Blueprint("api", url_prefix="/api")

        @bp.put("/items/<item_id:int>")
        async def update_item(request, item_id):
            return make_json({"updated": item_id})

        app.blueprint(bp)
        resp = client.put("/api/items/5")
        assert resp.json == {"updated": 5}

    def test_blueprint_delete(self, app, client):
        bp = Blueprint("api", url_prefix="/api")

        @bp.delete("/items/<item_id:int>")
        async def del_item(request, item_id):
            return make_empty()

        app.blueprint(bp)
        resp = client.delete("/api/items/3")
        assert resp.status == 204

    def test_blueprint_multiple_methods(self, app, client):
        bp = Blueprint("api", url_prefix="/api")

        @bp.route("/resource", methods=["GET", "POST"])
        async def resource(request):
            return make_json({"method": request.method})

        app.blueprint(bp)
        assert client.get("/api/resource").json == {"method": "GET"}
        assert client.post("/api/resource").json == {"method": "POST"}


class TestMultipleBlueprints:
    def test_register_two_blueprints(self, app, client):
        users_bp = Blueprint("users", url_prefix="/users")
        products_bp = Blueprint("products", url_prefix="/products")

        @users_bp.get("/all")
        async def all_users(request):
            return make_json({"type": "users"})

        @products_bp.get("/all")
        async def all_products(request):
            return make_json({"type": "products"})

        app.blueprint(users_bp)
        app.blueprint(products_bp)

        assert client.get("/users/all").json == {"type": "users"}
        assert client.get("/products/all").json == {"type": "products"}


class TestBlueprintMiddleware:
    def test_bp_middleware_only_runs_for_bp_routes(self, app, client):
        bp = Blueprint("bp", url_prefix="/bp")
        bp_mw_called = []

        @bp.on_request
        async def bp_mw(request):
            bp_mw_called.append(True)

        @bp.get("/endpoint")
        async def bp_handler(request):
            return make_text("bp_response")

        @app.get("/app-endpoint")
        async def app_handler(request):
            return make_text("app_response")

        app.blueprint(bp)

        resp = client.get("/bp/endpoint")
        assert resp.status == 200
        assert resp.text == "bp_response"
        assert len(bp_mw_called) == 1

        bp_mw_called.clear()
        resp = client.get("/app-endpoint")
        assert resp.status == 200
        assert len(bp_mw_called) == 0

    def test_bp_request_mw_can_short_circuit(self, app, client):
        bp = Blueprint("bp", url_prefix="/bp")

        @bp.on_request
        async def block(request):
            return make_text("blocked", status=403)

        @bp.get("/secret")
        async def handler(request):
            return make_text("should not reach")

        app.blueprint(bp)
        resp = client.get("/bp/secret")
        assert resp.status == 403
        assert resp.text == "blocked"

    def test_bp_response_mw_modifies_response(self, app, client):
        bp = Blueprint("bp", url_prefix="/bp")

        @bp.on_response
        async def add_header(request, response):
            response.headers["x-bp"] = "yes"

        @bp.get("/data")
        async def handler(request):
            return make_json({"ok": True})

        app.blueprint(bp)
        resp = client.get("/bp/data")
        assert resp.headers.get("x-bp") == "yes"


class TestBlueprintGroup:
    def test_group_adds_prefix(self, app, client):
        bp1 = Blueprint("v1_users", url_prefix="/users")
        bp2 = Blueprint("v1_items", url_prefix="/items")

        @bp1.get("/list")
        async def users(request):
            return make_json({"type": "users"})

        @bp2.get("/list")
        async def items(request):
            return make_json({"type": "items"})

        grp = blueprint_group(bp1, bp2, url_prefix="/api/v1")
        app.blueprint(grp)

        assert client.get("/api/v1/users/list").json == {"type": "users"}
        assert client.get("/api/v1/items/list").json == {"type": "items"}

    def test_register_list_of_blueprints(self, app, client):
        bp1 = Blueprint("a", url_prefix="/a")
        bp2 = Blueprint("b", url_prefix="/b")

        @bp1.get("/x")
        async def handler_a(request):
            return make_text("a")

        @bp2.get("/x")
        async def handler_b(request):
            return make_text("b")

        app.blueprint([bp1, bp2])

        assert client.get("/a/x").text == "a"
        assert client.get("/b/x").text == "b"


class TestBlueprintErrorHandlers:
    def test_bp_exception_handler(self, app, client):
        bp = Blueprint("bp", url_prefix="/bp")

        @bp.exception(ValueError)
        async def handle_value_error(request, exc):
            return make_json({"error": "bad value"}, status=400)

        @bp.get("/fail")
        async def handler(request):
            raise ValueError("oops")

        app.blueprint(bp)
        resp = client.get("/bp/fail")
        assert resp.status == 400
        assert resp.json == {"error": "bad value"}
