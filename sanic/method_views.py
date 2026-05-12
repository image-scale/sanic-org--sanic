import asyncio
from functools import wraps

from .errors import InvalidMethod


class MethodBasedView:
    decorators = []

    def __init_subclass__(cls, attach=None, uri=None, methods=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if attach is not None and uri is not None:
            cls.attach_to(attach, uri, methods=methods)

    @classmethod
    def attach_to(cls, target, uri, methods=None, name=None, **kwargs):
        handler = cls.as_handler()
        if methods is None:
            methods = cls._get_supported_methods()
        target.route(uri, methods=list(methods), name=name, **kwargs)(handler)

    @classmethod
    def _get_supported_methods(cls):
        methods = []
        for method_name in ("get", "post", "put", "patch", "delete",
                            "head", "options"):
            if hasattr(cls, method_name) and callable(getattr(cls, method_name)):
                methods.append(method_name.upper())
        return methods

    @classmethod
    def as_handler(cls):
        async def view_handler(request, **kwargs):
            instance = cls()
            return await instance.dispatch(request, **kwargs)

        if cls.decorators:
            for decorator in reversed(cls.decorators):
                view_handler = decorator(view_handler)

        view_handler.__name__ = cls.__name__
        view_handler.__qualname__ = cls.__qualname__

        return view_handler

    async def dispatch(self, request, **kwargs):
        method = request.method.lower()
        handler = getattr(self, method, None)
        if handler is None:
            supported = self._get_supported_methods()
            raise InvalidMethod(
                f"Method {request.method} not allowed",
                method=request.method,
                allowed=supported,
            )
        result = handler(request, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return result
