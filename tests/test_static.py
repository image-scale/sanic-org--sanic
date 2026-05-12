import os
import tempfile
import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.static import guess_content_type, _resolve_file, _find_index


@pytest.fixture
def static_dir():
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "test.txt"), "w") as f:
            f.write("hello world")
        with open(os.path.join(d, "data.json"), "w") as f:
            f.write('{"key": "value"}')
        with open(os.path.join(d, "page.html"), "w") as f:
            f.write("<h1>Hello</h1>")
        with open(os.path.join(d, "image.png"), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
        with open(os.path.join(d, "script.js"), "w") as f:
            f.write("console.log('hi');")
        sub = os.path.join(d, "sub")
        os.makedirs(sub)
        with open(os.path.join(sub, "nested.txt"), "w") as f:
            f.write("nested content")
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write("<h1>Index</h1>")
        yield d


@pytest.fixture
def static_app(static_dir):
    app = Sanic("static_test")
    yield app
    Sanic._registry.pop("static_test", None)


@pytest.fixture
def static_client(static_app):
    return AppTestClient(static_app)


class TestGuessContentType:
    def test_text_file(self):
        ct = guess_content_type("file.txt")
        assert "text/plain" in ct
        assert "charset=utf-8" in ct

    def test_json_file(self):
        ct = guess_content_type("file.json")
        assert "application/json" in ct

    def test_html_file(self):
        ct = guess_content_type("file.html")
        assert "text/html" in ct
        assert "charset=utf-8" in ct

    def test_png_file(self):
        ct = guess_content_type("file.png")
        assert ct == "image/png"

    def test_javascript_file(self):
        ct = guess_content_type("file.js")
        assert "javascript" in ct
        assert "charset=utf-8" in ct

    def test_unknown_extension(self):
        ct = guess_content_type("file.xyz123unknown")
        assert ct == "application/octet-stream"

    def test_custom_fallback(self):
        ct = guess_content_type("file.xyz123unknown", fallback="text/plain")
        assert ct == "text/plain"


class TestResolveFile:
    def test_resolve_existing_file(self, static_dir):
        resolved, is_dir = _resolve_file(static_dir, "test.txt")
        assert resolved.name == "test.txt"
        assert not is_dir

    def test_resolve_nested_file(self, static_dir):
        resolved, is_dir = _resolve_file(static_dir, "sub/nested.txt")
        assert resolved.name == "nested.txt"
        assert not is_dir

    def test_resolve_directory(self, static_dir):
        resolved, is_dir = _resolve_file(static_dir, "sub")
        assert is_dir

    def test_path_traversal_blocked(self, static_dir):
        from sanic.errors import PathNotFound
        with pytest.raises(PathNotFound):
            _resolve_file(static_dir, "../etc/passwd")


class TestFindIndex:
    def test_finds_index_html(self, static_dir):
        result = _find_index(static_dir, "index.html")
        assert result is not None
        assert result.name == "index.html"

    def test_returns_none_when_not_found(self, static_dir):
        result = _find_index(static_dir, "nonexistent.html")
        assert result is None

    def test_list_of_index_files(self, static_dir):
        result = _find_index(static_dir, ["default.html", "index.html"])
        assert result is not None
        assert result.name == "index.html"


class TestStaticFileServing:
    def test_serve_text_file(self, static_app, static_client, static_dir):
        static_app.static("/files", static_dir)
        resp = static_client.get("/files/test.txt")
        assert resp.status == 200
        assert resp.text == "hello world"
        assert "text/plain" in resp.content_type

    def test_serve_json_file(self, static_app, static_client, static_dir):
        static_app.static("/files", static_dir)
        resp = static_client.get("/files/data.json")
        assert resp.status == 200
        assert resp.json == {"key": "value"}

    def test_serve_html_file(self, static_app, static_client, static_dir):
        static_app.static("/files", static_dir)
        resp = static_client.get("/files/page.html")
        assert resp.status == 200
        assert "<h1>Hello</h1>" in resp.text
        assert "text/html" in resp.content_type

    def test_serve_binary_file(self, static_app, static_client, static_dir):
        static_app.static("/files", static_dir)
        resp = static_client.get("/files/image.png")
        assert resp.status == 200
        assert resp.body.startswith(b"\x89PNG")
        assert resp.content_type == "image/png"

    def test_serve_nested_file(self, static_app, static_client, static_dir):
        static_app.static("/files", static_dir)
        resp = static_client.get("/files/sub/nested.txt")
        assert resp.status == 200
        assert resp.text == "nested content"

    def test_file_not_found(self, static_app, static_client, static_dir):
        static_app.static("/files", static_dir)
        resp = static_client.get("/files/nonexistent.txt")
        assert resp.status == 404

    def test_custom_url_prefix(self, static_app, static_client, static_dir):
        static_app.static("/assets", static_dir, name="assets")
        resp = static_client.get("/assets/test.txt")
        assert resp.status == 200
        assert resp.text == "hello world"

    def test_forced_content_type(self, static_app, static_client, static_dir):
        static_app.static("/files", static_dir, name="forced",
                          content_type="text/plain")
        resp = static_client.get("/files/data.json")
        assert resp.status == 200
        assert "text/plain" in resp.content_type

    def test_directory_index(self, static_app, static_client, static_dir):
        static_app.static("/site", static_dir, name="site",
                          index="index.html")
        resp = static_client.get("/site")
        assert resp.status == 200
        assert "<h1>Index</h1>" in resp.text

    def test_directory_index_list(self, static_app, static_client, static_dir):
        static_app.static("/site2", static_dir, name="site2",
                          index=["default.html", "index.html"])
        resp = static_client.get("/site2")
        assert resp.status == 200
        assert "<h1>Index</h1>" in resp.text

    def test_directory_without_index_returns_404(self, static_app, static_client, static_dir):
        static_app.static("/noindex", static_dir, name="noindex")
        resp = static_client.get("/noindex")
        assert resp.status == 404

    def test_subdirectory_without_index_returns_404(self, static_app, static_client, static_dir):
        static_app.static("/files2", static_dir, name="files2")
        resp = static_client.get("/files2/sub")
        assert resp.status == 404


class TestStaticSingleFile:
    def test_serve_single_file(self, static_app, static_client, static_dir):
        filepath = os.path.join(static_dir, "test.txt")
        static_app.static("/readme", filepath, name="readme")
        resp = static_client.get("/readme")
        assert resp.status == 200
        assert resp.text == "hello world"


class TestStaticWithBlueprint:
    def test_blueprint_static(self, static_dir):
        from sanic.blueprints import Blueprint
        app = Sanic("bp_static_test")
        bp = Blueprint("docs", url_prefix="/docs")
        bp.static("/files", static_dir)
        app.blueprint(bp)
        client = AppTestClient(app)
        resp = client.get("/docs/files/test.txt")
        assert resp.status == 200
        assert resp.text == "hello world"
        Sanic._registry.pop("bp_static_test", None)
