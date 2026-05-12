import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import make_json, make_text
from sanic.cookie_utils import (
    parse_request_cookies, ResponseCookie, ResponseCookieJar,
)


class TestRequestCookieParsing:
    def test_parse_simple_cookie(self, app, client):
        @app.get("/cookies")
        async def handler(request):
            name = request.cookies.get("session", "none")
            return make_json({"session": name})

        resp = client.get("/cookies", headers={"Cookie": "session=abc123"})
        assert resp.json == {"session": "abc123"}

    def test_parse_multiple_cookies(self, app, client):
        @app.get("/cookies")
        async def handler(request):
            return make_json({
                "a": request.cookies.get("a", ""),
                "b": request.cookies.get("b", ""),
            })

        resp = client.get("/cookies",
                          headers={"Cookie": "a=one; b=two"})
        assert resp.json == {"a": "one", "b": "two"}

    def test_parse_empty_cookie_header(self, app, client):
        @app.get("/cookies")
        async def handler(request):
            return make_json({"count": len(request.cookies)})

        resp = client.get("/cookies")
        assert resp.json == {"count": 0}

    def test_parse_quoted_value(self):
        result = parse_request_cookies('key="quoted value"')
        assert result["key"] == "quoted value"

    def test_parse_function_directly(self):
        result = parse_request_cookies("name=alice; token=xyz; lang=en")
        assert result == {"name": "alice", "token": "xyz", "lang": "en"}


class TestResponseCookieSetting:
    def test_add_cookie_to_response(self, app, client):
        @app.get("/set-cookie")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("session", "abc123")
            return resp

        resp = client.get("/set-cookie")
        assert resp.status == 200
        assert "session" in resp.cookies
        assert resp.cookies["session"] == "abc123"

    def test_cookie_with_path(self, app, client):
        @app.get("/set-cookie")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("id", "42", path="/api")
            return resp

        resp = client.get("/set-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "Path=/api" in cookie_str

    def test_cookie_with_domain(self, app, client):
        @app.get("/set-cookie")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("id", "42", domain="example.com")
            return resp

        resp = client.get("/set-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "Domain=example.com" in cookie_str

    def test_cookie_secure_flag(self, app, client):
        @app.get("/set-cookie")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("token", "xyz", secure=True)
            return resp

        resp = client.get("/set-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "Secure" in cookie_str

    def test_cookie_httponly_flag(self, app, client):
        @app.get("/set-cookie")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("token", "xyz", httponly=True)
            return resp

        resp = client.get("/set-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "HttpOnly" in cookie_str

    def test_cookie_samesite(self, app, client):
        @app.get("/set-cookie")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("token", "xyz", samesite="Strict")
            return resp

        resp = client.get("/set-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "SameSite=Strict" in cookie_str

    def test_cookie_max_age(self, app, client):
        @app.get("/set-cookie")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("token", "xyz", max_age=3600)
            return resp

        resp = client.get("/set-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "Max-Age=3600" in cookie_str

    def test_cookie_expires(self, app, client):
        from datetime import datetime
        @app.get("/set-cookie")
        async def handler(request):
            resp = make_text("ok")
            exp = datetime(2030, 1, 1, 0, 0, 0)
            resp.add_cookie("token", "xyz", expires=exp)
            return resp

        resp = client.get("/set-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "Expires=" in cookie_str


class TestDeleteCookie:
    def test_delete_cookie(self, app, client):
        @app.get("/delete-cookie")
        async def handler(request):
            resp = make_text("deleted")
            resp.delete_cookie("session")
            return resp

        resp = client.get("/delete-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "Max-Age=0" in cookie_str
        assert "session" in cookie_str


class TestCookiePrefixes:
    def test_host_prefix(self):
        cookie = ResponseCookie("id", "123", host_prefix=True)
        assert cookie.encoded_key == "__Host-id"
        assert cookie.secure is True
        assert cookie.path == "/"
        assert cookie.domain is None

    def test_secure_prefix(self):
        cookie = ResponseCookie("id", "123", secure_prefix=True)
        assert cookie.encoded_key == "__Secure-id"
        assert cookie.secure is True

    def test_host_prefix_in_header(self, app, client):
        @app.get("/host-cookie")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("session", "val", host_prefix=True)
            return resp

        resp = client.get("/host-cookie")
        cookie_str = resp.raw_cookies[0]
        assert "__Host-session=" in cookie_str


class TestCookieJar:
    def test_jar_has_cookie(self):
        jar = ResponseCookieJar()
        jar.add("key", "value")
        assert jar.has("key")
        assert not jar.has("other")

    def test_jar_length(self):
        jar = ResponseCookieJar()
        jar.add("a", "1")
        jar.add("b", "2")
        assert len(jar) == 2

    def test_jar_header_values(self):
        jar = ResponseCookieJar()
        jar.add("token", "abc", secure=False, samesite="Lax")
        values = jar.header_values()
        assert len(values) == 1
        assert "token=abc" in values[0]

    def test_multiple_response_cookies(self, app, client):
        @app.get("/multi")
        async def handler(request):
            resp = make_text("ok")
            resp.add_cookie("a", "1", secure=False, samesite="")
            resp.add_cookie("b", "2", secure=False, samesite="")
            return resp

        resp = client.get("/multi")
        assert len(resp.raw_cookies) == 2
        assert resp.cookies["a"] == "1"
        assert resp.cookies["b"] == "2"
