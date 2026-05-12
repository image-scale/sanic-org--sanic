import asyncio
import json as json_lib
import traceback
from collections import defaultdict
from functools import partial
from typing import Any, Callable, Optional, Dict, Iterable

from .routing import AppRouter
from .request_type import RequestData
from .response_types import (
    ServerResponse, make_json, make_text, make_html,
)
from .errors import (
    FrameworkError, PathNotFound, InvalidMethod, BadRequestError,
)
from .http_constants import HttpMethod, ALL_HTTP_METHODS
from .configuration import AppConfig
from .signals import SignalDispatcher, LifecycleEvent
from .static import register_static


class Sanic:
    _registry = {}
    test_mode = False

    def __init__(self, name, router=None, env_prefix=None,
                 request_class=None, strict_slashes=False,
                 dumps=None, loads=None, config=None):
        self.name = name
        self.router = router or AppRouter()
        self.strict_slashes = strict_slashes
        self.request_class = request_class or RequestData
        self._dumps = dumps or json_lib.dumps
        self._loads = loads or json_lib.loads
        self.env_prefix = env_prefix or "SANIC_"

        self.config = config or AppConfig(env_prefix=self.env_prefix)

        self.request_middleware = []
        self.response_middleware = []
        self._request_mw_entries = []
        self._response_mw_entries = []
        self._mw_sequence = 0
        self.error_handlers = {}
        self.listeners = defaultdict(list)
        self.blueprints = {}
        self.signal_router = SignalDispatcher()

        Sanic._registry[name] = self

    @classmethod
    def get_app(cls, name, force_create=False):
        if name in cls._registry:
            return cls._registry[name]
        if force_create:
            return cls(name)
        raise LookupError(f"Sanic app '{name}' not found.")

    def route(self, uri, methods=None, host=None, strict_slashes=None,
              name=None, version=None, version_prefix="/v"):
        if methods is None:
            methods = ["GET"]

        def decorator(handler):
            final_uri = uri
            if version is not None:
                final_uri = f"{version_prefix}{version}{uri}"
            self.router.add(
                final_uri, handler, methods, name=name, host=host,
                strict_slashes=strict_slashes if strict_slashes is not None
                else self.strict_slashes,
            )
            return handler
        return decorator

    def get(self, uri, host=None, strict_slashes=None, name=None,
            version=None, version_prefix="/v"):
        return self.route(uri, methods=["GET"], host=host,
                          strict_slashes=strict_slashes, name=name,
                          version=version, version_prefix=version_prefix)

    def post(self, uri, host=None, strict_slashes=None, name=None,
             version=None, version_prefix="/v"):
        return self.route(uri, methods=["POST"], host=host,
                          strict_slashes=strict_slashes, name=name,
                          version=version, version_prefix=version_prefix)

    def put(self, uri, host=None, strict_slashes=None, name=None,
            version=None, version_prefix="/v"):
        return self.route(uri, methods=["PUT"], host=host,
                          strict_slashes=strict_slashes, name=name,
                          version=version, version_prefix=version_prefix)

    def delete(self, uri, host=None, strict_slashes=None, name=None,
               version=None, version_prefix="/v"):
        return self.route(uri, methods=["DELETE"], host=host,
                          strict_slashes=strict_slashes, name=name,
                          version=version, version_prefix=version_prefix)

    def patch(self, uri, host=None, strict_slashes=None, name=None,
              version=None, version_prefix="/v"):
        return self.route(uri, methods=["PATCH"], host=host,
                          strict_slashes=strict_slashes, name=name,
                          version=version, version_prefix=version_prefix)

    def head(self, uri, host=None, strict_slashes=None, name=None,
             version=None, version_prefix="/v"):
        return self.route(uri, methods=["HEAD"], host=host,
                          strict_slashes=strict_slashes, name=name,
                          version=version, version_prefix=version_prefix)

    def options(self, uri, host=None, strict_slashes=None, name=None,
                version=None, version_prefix="/v"):
        return self.route(uri, methods=["OPTIONS"], host=host,
                          strict_slashes=strict_slashes, name=name,
                          version=version, version_prefix=version_prefix)

    def middleware(self, middleware_or_request=None, attach_to="request",
                   *, priority=0):
        def register(func):
            self._mw_sequence += 1
            seq = self._mw_sequence
            if attach_to == "request":
                self._request_mw_entries.append((priority, seq, func))
                self._request_mw_entries.sort(
                    key=lambda e: (-e[0], e[1])
                )
                self.request_middleware = [e[2] for e in self._request_mw_entries]
            else:
                self._response_mw_entries.append((priority, seq, func))
                self._response_mw_entries.sort(
                    key=lambda e: (-e[0], -e[1])
                )
                self.response_middleware = [e[2] for e in self._response_mw_entries]
            return func

        if callable(middleware_or_request):
            return register(middleware_or_request)

        if isinstance(middleware_or_request, str):
            attach_to = middleware_or_request

        def decorator(func):
            return register(func)
        return decorator

    def on_request(self, func=None, *, priority=0):
        def register(f):
            return self.middleware(f, attach_to="request", priority=priority)
        if func is not None:
            return register(func)
        return register

    def on_response(self, func=None, *, priority=0):
        def register(f):
            return self.middleware(f, attach_to="response", priority=priority)
        if func is not None:
            return register(func)
        return register

    def exception(self, *exceptions):
        def decorator(handler):
            for exc_class in exceptions:
                self.error_handlers[exc_class] = handler
            return handler
        return decorator

    def listener(self, event_or_handler=None, event_name=None, *, priority=0):
        def register(handler, event):
            self.listeners[event].append(handler)
            self.signal_router.register(event, handler, priority=priority)
            return handler

        if callable(event_or_handler):
            ev = event_name or LifecycleEvent.BEFORE_SERVER_START
            return register(event_or_handler, ev)

        if isinstance(event_or_handler, str):
            event = event_or_handler
        else:
            event = event_name or LifecycleEvent.BEFORE_SERVER_START

        def decorator(handler):
            return register(handler, event)
        return decorator

    def before_server_start(self, func=None, *, priority=0):
        return self.listener(func, event_name=LifecycleEvent.BEFORE_SERVER_START,
                             priority=priority)

    def after_server_start(self, func=None, *, priority=0):
        return self.listener(func, event_name=LifecycleEvent.AFTER_SERVER_START,
                             priority=priority)

    def before_server_stop(self, func=None, *, priority=0):
        return self.listener(func, event_name=LifecycleEvent.BEFORE_SERVER_STOP,
                             priority=priority)

    def after_server_stop(self, func=None, *, priority=0):
        return self.listener(func, event_name=LifecycleEvent.AFTER_SERVER_STOP,
                             priority=priority)

    def signal(self, event_name):
        def decorator(handler):
            self.signal_router.register(event_name, handler)
            return handler
        return decorator

    async def dispatch_signal(self, event_name, **kwargs):
        await self.signal_router.dispatch(event_name, **kwargs)

    def static(self, uri, file_or_directory, name="static",
               content_type=None, index=None, strict_slashes=None):
        register_static(self, uri, file_or_directory, name=name,
                         content_type=content_type, index=index,
                         strict_slashes=strict_slashes)

    async def handle_request(self, request):
        try:
            for mw in self.request_middleware:
                resp = mw(request)
                if asyncio.iscoroutine(resp):
                    resp = await resp
                if resp is not None:
                    return resp

            route, handler, params = self.router.resolve(
                request.method, request.path
            )
            request.match_info = params
            request.route = route

            resp = handler(request, **params)
            if asyncio.iscoroutine(resp):
                resp = await resp

            for mw in self.response_middleware:
                mw_result = mw(request, resp)
                if asyncio.iscoroutine(mw_result):
                    mw_result = await mw_result
                if mw_result is not None:
                    resp = mw_result

            return resp

        except FrameworkError as exc:
            return await self._handle_error(request, exc)
        except Exception as exc:
            return await self._handle_error(request, exc)

    async def _handle_error(self, request, exc):
        exc_type = type(exc)
        for cls in exc_type.__mro__:
            if cls in self.error_handlers:
                handler = self.error_handlers[cls]
                resp = handler(request, exc)
                if asyncio.iscoroutine(resp):
                    resp = await resp
                return resp

        status = getattr(exc, "status_code", 500)
        message = str(exc) if str(exc) else "Internal Server Error"

        if isinstance(exc, InvalidMethod):
            body = {"error": message, "allowed_methods": exc.allowed}
            resp = make_json(body, status=status)
            resp.headers["allow"] = ", ".join(exc.allowed)
            return resp

        return make_json({"error": message}, status=status)

    def url_for(self, view_name, **kwargs):
        return self.router.url_for(view_name, **kwargs)

    def blueprint(self, bp):
        from .blueprints import BlueprintGroup
        if isinstance(bp, (list, tuple)):
            for b in bp:
                self.blueprint(b)
            return
        if isinstance(bp, BlueprintGroup):
            bp.register(self)
            return
        bp.register(self)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                msg = await receive()
                if msg["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif msg["type"] == "lifespan.shutdown":
                    await send({"type": "lifespan.shutdown.complete"})
                    return
        elif scope["type"] == "http":
            await self._handle_asgi_http(scope, receive, send)

    async def _handle_asgi_http(self, scope, receive, send):
        body_parts = []
        while True:
            msg = await receive()
            body_parts.append(msg.get("body", b""))
            if not msg.get("more_body", False):
                break
        body = b"".join(body_parts)

        raw_path = scope.get("path", "/")
        qs = scope.get("query_string", b"").decode("utf-8", errors="replace")
        headers = {}
        for hname, hval in scope.get("headers", []):
            headers[hname.decode("latin-1").lower()] = hval.decode("latin-1")
        method = scope.get("method", "GET")

        request = self.request_class(
            method=method,
            path=raw_path,
            headers=headers,
            body=body,
            query_string=qs,
            app=self,
        )

        response = await self.handle_request(request)

        resp_headers = []
        if response and hasattr(response, "headers"):
            for k, v in response.headers.items():
                resp_headers.append(
                    (k.encode("latin-1"), str(v).encode("latin-1"))
                )
            if hasattr(response, "cookie_jar"):
                for cookie_val in response.cookie_jar.header_values():
                    resp_headers.append(
                        (b"set-cookie", cookie_val.encode("latin-1"))
                    )

        status = response.status if response else 500
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": resp_headers,
        })
        await send({
            "type": "http.response.body",
            "body": response.body if response else b"",
        })
