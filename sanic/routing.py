import re
import uuid
from collections import defaultdict

from .errors import PathNotFound, InvalidMethod


class RouteEntry:
    def __init__(self, uri, handler, methods, name=None, host=None,
                 strict_slashes=False):
        self.uri = uri
        self.handler = handler
        self.methods = {m.upper() for m in methods}
        self.name = name or handler.__name__
        self.host = host
        self.strict_slashes = strict_slashes
        self.param_names = []
        self.param_types = {}
        self.pattern = self._compile_pattern(uri)

    def _compile_pattern(self, uri):
        param_re = re.compile(r"<(\w+)(?::(\w+))?>")
        parts = []
        last_end = 0
        for match in param_re.finditer(uri):
            parts.append(re.escape(uri[last_end:match.start()]))
            pname = match.group(1)
            ptype = match.group(2) or "str"
            self.param_names.append(pname)
            self.param_types[pname] = ptype
            if ptype == "int":
                parts.append(r"(-?\d+)")
            elif ptype == "float":
                parts.append(r"(-?[\d.]+)")
            elif ptype == "uuid":
                parts.append(r"([a-f0-9\-]{36})")
            elif ptype == "path":
                parts.append(r"(.+)")
            else:
                parts.append(r"([^/]+)")
            last_end = match.end()
        parts.append(re.escape(uri[last_end:]))
        full_pattern = "^" + "".join(parts) + "$"
        return re.compile(full_pattern)

    def match(self, path):
        m = self.pattern.match(path)
        if not m:
            return None
        params = {}
        for i, name in enumerate(self.param_names):
            raw = m.group(i + 1)
            ptype = self.param_types[name]
            if ptype == "int":
                params[name] = int(raw)
            elif ptype == "float":
                params[name] = float(raw)
            elif ptype == "uuid":
                params[name] = uuid.UUID(raw)
            else:
                params[name] = raw
        return params

    def _convert_param(self, value, ptype):
        if ptype == "int":
            return int(value)
        elif ptype == "float":
            return float(value)
        elif ptype == "uuid":
            return uuid.UUID(value)
        return value


class AppRouter:
    def __init__(self):
        self.routes = []
        self._name_index = {}

    def add(self, uri, handler, methods, name=None, host=None,
            strict_slashes=False):
        if not uri.startswith("/"):
            uri = "/" + uri
        route = RouteEntry(uri, handler, methods, name=name, host=host,
                           strict_slashes=strict_slashes)
        self.routes.append(route)
        self._name_index[route.name] = route
        return route

    def resolve(self, method, path):
        method = method.upper()
        matched_routes = []
        for route in self.routes:
            params = route.match(path)
            if params is not None:
                matched_routes.append((route, params))

        if not matched_routes:
            raise PathNotFound(f"No route found for path: {path}")

        for route, params in matched_routes:
            if method in route.methods:
                return route, route.handler, params

        allowed = set()
        for route, _ in matched_routes:
            allowed.update(route.methods)
        raise InvalidMethod(
            f"Method {method} not allowed for path: {path}",
            method=method,
            allowed=sorted(allowed),
        )

    def find_by_name(self, name):
        return self._name_index.get(name)

    def url_for(self, name, **kwargs):
        route = self._name_index.get(name)
        if route is None:
            raise PathNotFound(f"No route with name: {name}")
        uri = route.uri
        param_re = re.compile(r"<(\w+)(?::(\w+))?>")
        used_params = set()
        def replacer(m):
            pname = m.group(1)
            if pname in kwargs:
                used_params.add(pname)
                return str(kwargs[pname])
            return m.group(0)
        result = param_re.sub(replacer, uri)

        extra = {k: v for k, v in kwargs.items() if k not in used_params}
        if extra:
            from urllib.parse import urlencode
            result += "?" + urlencode(extra)
        return result
