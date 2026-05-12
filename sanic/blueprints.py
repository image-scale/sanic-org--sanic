import asyncio
from collections import defaultdict


class Blueprint:
    def __init__(self, name, url_prefix="", strict_slashes=False,
                 version=None, version_prefix="/v"):
        self.name = name
        self.url_prefix = url_prefix
        self.strict_slashes = strict_slashes
        self.version = version
        self.version_prefix = version_prefix
        self._deferred_routes = []
        self._deferred_middleware = []
        self._deferred_error_handlers = []
        self.request_middleware = []
        self.response_middleware = []
        self._request_mw_entries = []
        self._response_mw_entries = []
        self._mw_sequence = 0
        self.error_handlers = {}

    def route(self, uri, methods=None, host=None, strict_slashes=None,
              name=None, version=None, version_prefix=None):
        if methods is None:
            methods = ["GET"]

        def decorator(handler):
            self._deferred_routes.append({
                "uri": uri,
                "handler": handler,
                "methods": methods,
                "name": name,
                "host": host,
                "strict_slashes": strict_slashes,
                "version": version,
                "version_prefix": version_prefix,
            })
            return handler
        return decorator

    def get(self, uri, **kwargs):
        return self.route(uri, methods=["GET"], **kwargs)

    def post(self, uri, **kwargs):
        return self.route(uri, methods=["POST"], **kwargs)

    def put(self, uri, **kwargs):
        return self.route(uri, methods=["PUT"], **kwargs)

    def delete(self, uri, **kwargs):
        return self.route(uri, methods=["DELETE"], **kwargs)

    def patch(self, uri, **kwargs):
        return self.route(uri, methods=["PATCH"], **kwargs)

    def head(self, uri, **kwargs):
        return self.route(uri, methods=["HEAD"], **kwargs)

    def options(self, uri, **kwargs):
        return self.route(uri, methods=["OPTIONS"], **kwargs)

    def middleware(self, middleware_or_request=None, attach_to="request",
                   *, priority=0):
        def register(func):
            self._mw_sequence += 1
            seq = self._mw_sequence
            if attach_to == "request":
                self._request_mw_entries.append((priority, seq, func))
                self._request_mw_entries.sort(key=lambda e: (-e[0], e[1]))
                self.request_middleware = [e[2] for e in self._request_mw_entries]
            else:
                self._response_mw_entries.append((priority, seq, func))
                self._response_mw_entries.sort(key=lambda e: (-e[0], -e[1]))
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

    def register(self, app, url_prefix=None):
        prefix = url_prefix if url_prefix is not None else self.url_prefix
        app.blueprints[self.name] = self

        for route_info in self._deferred_routes:
            uri = prefix + route_info["uri"]
            v = route_info.get("version") or self.version
            vp = route_info.get("version_prefix") or self.version_prefix
            if v is not None:
                uri = f"{vp}{v}{uri}"
            route_name = route_info.get("name")
            if route_name:
                full_name = f"{self.name}.{route_name}"
            else:
                full_name = f"{self.name}.{route_info['handler'].__name__}"

            original_handler = route_info["handler"]
            bp = self

            async def make_bp_handler(handler, blueprint):
                async def bp_handler(request, **kwargs):
                    for mw in blueprint.request_middleware:
                        resp = mw(request)
                        if asyncio.iscoroutine(resp):
                            resp = await resp
                        if resp is not None:
                            return resp

                    resp = handler(request, **kwargs)
                    if asyncio.iscoroutine(resp):
                        resp = await resp

                    for mw in blueprint.response_middleware:
                        mw_result = mw(request, resp)
                        if asyncio.iscoroutine(mw_result):
                            mw_result = await mw_result
                        if mw_result is not None:
                            resp = mw_result

                    return resp
                return bp_handler

            wrapped = _create_bp_handler(original_handler, bp)

            app.router.add(
                uri, wrapped, route_info["methods"],
                name=full_name, host=route_info.get("host"),
                strict_slashes=route_info.get("strict_slashes")
                if route_info.get("strict_slashes") is not None
                else self.strict_slashes,
            )

        for exc_class, handler in self.error_handlers.items():
            if exc_class not in app.error_handlers:
                app.error_handlers[exc_class] = handler


def _create_bp_handler(handler, blueprint):
    async def bp_handler(request, **kwargs):
        try:
            for mw in blueprint.request_middleware:
                resp = mw(request)
                if asyncio.iscoroutine(resp):
                    resp = await resp
                if resp is not None:
                    return resp

            resp = handler(request, **kwargs)
            if asyncio.iscoroutine(resp):
                resp = await resp

            for mw in blueprint.response_middleware:
                mw_result = mw(request, resp)
                if asyncio.iscoroutine(mw_result):
                    mw_result = await mw_result
                if mw_result is not None:
                    resp = mw_result

            return resp
        except Exception as exc:
            exc_type = type(exc)
            for cls in exc_type.__mro__:
                if cls in blueprint.error_handlers:
                    err_handler = blueprint.error_handlers[cls]
                    result = err_handler(request, exc)
                    if asyncio.iscoroutine(result):
                        result = await result
                    return result
            raise
    return bp_handler


class BlueprintGroup:
    def __init__(self, url_prefix="", version=None, version_prefix="/v"):
        self.url_prefix = url_prefix
        self.version = version
        self.version_prefix = version_prefix
        self.blueprints = []

    def append(self, bp):
        self.blueprints.append(bp)

    def register(self, app):
        for bp in self.blueprints:
            prefix = self.url_prefix + bp.url_prefix
            bp.register(app, url_prefix=prefix)

    def __iter__(self):
        return iter(self.blueprints)


def group(*blueprints, url_prefix="", version=None, version_prefix="/v"):
    grp = BlueprintGroup(url_prefix=url_prefix, version=version,
                         version_prefix=version_prefix)
    for bp in blueprints:
        grp.append(bp)
    return grp
