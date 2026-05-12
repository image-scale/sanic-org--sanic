import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import make_json, make_text
from sanic.errors import (
    FrameworkError, PathNotFound, InvalidMethod, BadRequestError,
    AuthenticationError, PermissionDenied, InternalError,
)


class TestExceptionHandlerRegistration:
    def test_register_handler_with_decorator(self, app, client):
        @app.exception(ValueError)
        async def handle_value_error(request, exc):
            return make_json({"error": "bad value"}, status=400)

        @app.get("/fail")
        async def handler(request):
            raise ValueError("oops")

        resp = client.get("/fail")
        assert resp.status == 400
        assert resp.json == {"error": "bad value"}

    def test_handler_receives_request_and_exc(self, app, client):
        captured = {}

        @app.exception(RuntimeError)
        async def handle_runtime(request, exc):
            captured["path"] = request.path
            captured["msg"] = str(exc)
            return make_json({"caught": True}, status=500)

        @app.get("/boom")
        async def handler(request):
            raise RuntimeError("boom!")

        resp = client.get("/boom")
        assert captured["path"] == "/boom"
        assert captured["msg"] == "boom!"
        assert resp.json == {"caught": True}


class TestExceptionSpecificity:
    def test_subclass_handler_chosen_over_parent(self, app, client):
        class BaseError(Exception):
            pass

        class SpecificError(BaseError):
            pass

        @app.exception(BaseError)
        async def handle_base(request, exc):
            return make_json({"handler": "base"}, status=400)

        @app.exception(SpecificError)
        async def handle_specific(request, exc):
            return make_json({"handler": "specific"}, status=422)

        @app.get("/specific")
        async def handler(request):
            raise SpecificError("specific issue")

        resp = client.get("/specific")
        assert resp.status == 422
        assert resp.json == {"handler": "specific"}

    def test_parent_handler_catches_subclass(self, app, client):
        class CustomBase(Exception):
            pass

        class CustomChild(CustomBase):
            pass

        @app.exception(CustomBase)
        async def handle_base(request, exc):
            return make_json({"handler": "base"}, status=400)

        @app.get("/child")
        async def handler(request):
            raise CustomChild("child error")

        resp = client.get("/child")
        assert resp.status == 400
        assert resp.json == {"handler": "base"}


class TestBuiltInExceptions:
    def test_not_found_returns_404(self, app, client):
        resp = client.get("/nonexistent")
        assert resp.status == 404

    def test_method_not_allowed_returns_405(self, app, client):
        @app.get("/only-get")
        async def handler(request):
            return make_text("ok")

        resp = client.post("/only-get")
        assert resp.status == 405

    def test_framework_error_has_status_code(self):
        err = PathNotFound("not found")
        assert err.status_code == 404

    def test_bad_request_error(self):
        err = BadRequestError("bad input")
        assert err.status_code == 400

    def test_auth_error(self):
        err = AuthenticationError("unauthorized")
        assert err.status_code == 401

    def test_permission_denied(self):
        err = PermissionDenied("forbidden")
        assert err.status_code == 403

    def test_invalid_method(self):
        err = InvalidMethod("not allowed")
        assert err.status_code == 405

    def test_internal_error(self):
        err = InternalError("server error")
        assert err.status_code == 500

    def test_raise_framework_error_in_handler(self, app, client):
        @app.get("/error")
        async def handler(request):
            raise BadRequestError("invalid data")

        resp = client.get("/error")
        assert resp.status == 400


class TestDefaultErrorHandler:
    def test_default_returns_json_with_error(self, app, client):
        @app.get("/fail")
        async def handler(request):
            raise BadRequestError("bad request body")

        resp = client.get("/fail")
        assert resp.status == 400
        assert "error" in resp.json

    def test_unhandled_exception_returns_500(self, app, client):
        @app.get("/crash")
        async def handler(request):
            raise RuntimeError("unexpected crash")

        resp = client.get("/crash")
        assert resp.status == 500


class TestExceptionContextAndExtra:
    def test_framework_error_context(self):
        err = FrameworkError(
            "error",
            status_code=400,
            context={"field": "email"},
        )
        assert err.context == {"field": "email"}

    def test_framework_error_extra(self):
        err = FrameworkError(
            "error",
            extra={"debug": "info"},
        )
        assert err.extra == {"debug": "info"}

    def test_framework_error_headers(self):
        err = FrameworkError(
            "error",
            headers={"X-Rate-Limit": "exceeded"},
        )
        assert err.headers == {"X-Rate-Limit": "exceeded"}


class TestAsyncExceptionHandler:
    def test_async_handler(self, app, client):
        import asyncio

        @app.exception(TypeError)
        async def handle(request, exc):
            await asyncio.sleep(0)
            return make_json({"async": True}, status=400)

        @app.get("/type-err")
        async def handler(request):
            raise TypeError("wrong type")

        resp = client.get("/type-err")
        assert resp.status == 400
        assert resp.json == {"async": True}
