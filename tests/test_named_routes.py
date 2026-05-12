import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import make_json, make_text
from sanic.errors import PathNotFound
from sanic.blueprints import Blueprint


class TestNamedRoutes:
    def test_default_route_name(self):
        app = Sanic("named_1")

        @app.get("/hello")
        async def hello_handler(request):
            return make_text("hello")

        route = app.router.find_by_name("hello_handler")
        assert route is not None
        assert route.uri == "/hello"
        Sanic._registry.pop("named_1", None)

    def test_custom_route_name(self):
        app = Sanic("named_2")

        @app.get("/greet", name="greeting")
        async def handler(request):
            return make_text("hi")

        route = app.router.find_by_name("greeting")
        assert route is not None
        assert route.uri == "/greet"
        Sanic._registry.pop("named_2", None)

    def test_multiple_named_routes(self):
        app = Sanic("named_3")

        @app.get("/users", name="user_list")
        async def list_users(request):
            return make_json([])

        @app.get("/users/<user_id:int>", name="user_detail")
        async def get_user(request, user_id):
            return make_json({"id": user_id})

        assert app.router.find_by_name("user_list") is not None
        assert app.router.find_by_name("user_detail") is not None
        Sanic._registry.pop("named_3", None)

    def test_find_nonexistent_route(self):
        app = Sanic("named_4")
        result = app.router.find_by_name("nonexistent")
        assert result is None
        Sanic._registry.pop("named_4", None)


class TestUrlFor:
    def test_simple_url(self):
        app = Sanic("url_1")

        @app.get("/about", name="about")
        async def handler(request):
            return make_text("about")

        url = app.url_for("about")
        assert url == "/about"
        Sanic._registry.pop("url_1", None)

    def test_url_with_int_param(self):
        app = Sanic("url_2")

        @app.get("/users/<user_id:int>", name="user")
        async def handler(request, user_id):
            return make_json({"id": user_id})

        url = app.url_for("user", user_id=42)
        assert url == "/users/42"
        Sanic._registry.pop("url_2", None)

    def test_url_with_string_param(self):
        app = Sanic("url_3")

        @app.get("/posts/<slug>", name="post")
        async def handler(request, slug):
            return make_text(slug)

        url = app.url_for("post", slug="my-post")
        assert url == "/posts/my-post"
        Sanic._registry.pop("url_3", None)

    def test_url_with_multiple_params(self):
        app = Sanic("url_4")

        @app.get("/users/<user_id:int>/posts/<post_id:int>", name="user_post")
        async def handler(request, user_id, post_id):
            return make_json({"user": user_id, "post": post_id})

        url = app.url_for("user_post", user_id=5, post_id=10)
        assert url == "/users/5/posts/10"
        Sanic._registry.pop("url_4", None)

    def test_url_for_nonexistent_raises(self):
        app = Sanic("url_5")

        with pytest.raises(PathNotFound):
            app.url_for("nonexistent")
        Sanic._registry.pop("url_5", None)

    def test_url_with_extra_kwargs_as_query(self):
        app = Sanic("url_6")

        @app.get("/search", name="search")
        async def handler(request):
            return make_text("results")

        url = app.url_for("search", q="python", page=2)
        assert "/search?" in url
        assert "q=python" in url
        assert "page=2" in url
        Sanic._registry.pop("url_6", None)

    def test_url_with_mixed_path_and_query_params(self):
        app = Sanic("url_7")

        @app.get("/users/<user_id:int>/posts", name="user_posts")
        async def handler(request, user_id):
            return make_json([])

        url = app.url_for("user_posts", user_id=3, sort="date")
        assert url.startswith("/users/3/posts?")
        assert "sort=date" in url
        Sanic._registry.pop("url_7", None)


class TestUrlForInHandler:
    def test_url_for_from_request(self):
        app = Sanic("url_handler_1")

        @app.get("/home", name="home")
        async def home(request):
            return make_text("home")

        @app.get("/link", name="link")
        async def link(request):
            url = request.app.url_for("home")
            return make_json({"url": url})

        client = AppTestClient(app)
        resp = client.get("/link")
        assert resp.json["url"] == "/home"
        Sanic._registry.pop("url_handler_1", None)

    def test_url_for_with_params_from_handler(self):
        app = Sanic("url_handler_2")

        @app.get("/users/<user_id:int>", name="user_detail")
        async def user_detail(request, user_id):
            return make_json({"id": user_id})

        @app.get("/redirect-to-user/<user_id:int>")
        async def redirect_user(request, user_id):
            url = request.app.url_for("user_detail", user_id=user_id)
            return make_json({"redirect": url})

        client = AppTestClient(app)
        resp = client.get("/redirect-to-user/7")
        assert resp.json["redirect"] == "/users/7"
        Sanic._registry.pop("url_handler_2", None)


class TestBlueprintNamedRoutes:
    def test_blueprint_route_namespacing(self):
        app = Sanic("bp_name_1")
        bp = Blueprint("api", url_prefix="/api")

        @bp.get("/items", name="items")
        async def get_items(request):
            return make_json([])

        app.blueprint(bp)

        route = app.router.find_by_name("api.items")
        assert route is not None
        assert route.uri == "/api/items"
        Sanic._registry.pop("bp_name_1", None)

    def test_blueprint_url_for(self):
        app = Sanic("bp_name_2")
        bp = Blueprint("admin", url_prefix="/admin")

        @bp.get("/users/<user_id:int>", name="user")
        async def get_user(request, user_id):
            return make_json({"id": user_id})

        app.blueprint(bp)

        url = app.url_for("admin.user", user_id=99)
        assert url == "/admin/users/99"
        Sanic._registry.pop("bp_name_2", None)

    def test_blueprint_default_name(self):
        app = Sanic("bp_name_3")
        bp = Blueprint("blog", url_prefix="/blog")

        @bp.get("/posts")
        async def list_posts(request):
            return make_json([])

        app.blueprint(bp)

        route = app.router.find_by_name("blog.list_posts")
        assert route is not None
        Sanic._registry.pop("bp_name_3", None)

    def test_multiple_blueprints_namespacing(self):
        app = Sanic("bp_name_4")
        bp1 = Blueprint("users", url_prefix="/users")
        bp2 = Blueprint("posts", url_prefix="/posts")

        @bp1.get("/", name="list")
        async def list_users(request):
            return make_json([])

        @bp2.get("/", name="list")
        async def list_posts(request):
            return make_json([])

        app.blueprint(bp1)
        app.blueprint(bp2)

        assert app.router.find_by_name("users.list") is not None
        assert app.router.find_by_name("posts.list") is not None
        Sanic._registry.pop("bp_name_4", None)

    def test_blueprint_url_for_in_handler(self):
        app = Sanic("bp_name_5")
        bp = Blueprint("api", url_prefix="/api")

        @bp.get("/items/<item_id:int>", name="item")
        async def get_item(request, item_id):
            return make_json({"id": item_id})

        @bp.get("/link/<item_id:int>", name="link")
        async def link(request, item_id):
            url = request.app.url_for("api.item", item_id=item_id)
            return make_json({"url": url})

        app.blueprint(bp)
        client = AppTestClient(app)
        resp = client.get("/api/link/5")
        assert resp.json["url"] == "/api/items/5"
        Sanic._registry.pop("bp_name_5", None)


class TestRouteNameCollision:
    def test_later_route_overrides_name(self):
        app = Sanic("collision_1")

        @app.get("/first", name="page")
        async def first(request):
            return make_text("first")

        @app.get("/second", name="page")
        async def second(request):
            return make_text("second")

        url = app.url_for("page")
        assert url == "/second"
        Sanic._registry.pop("collision_1", None)
