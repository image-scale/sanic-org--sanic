import os


_BOOL_STRINGS = {
    "true": True, "1": True, "yes": True, "on": True,
    "false": False, "0": False, "no": False, "off": False,
}

_DEFAULTS = {
    "REQUEST_MAX_SIZE": 100_000_000,
    "REQUEST_TIMEOUT": 60,
    "RESPONSE_TIMEOUT": 60,
    "KEEP_ALIVE": True,
    "KEEP_ALIVE_TIMEOUT": 120,
    "ACCESS_LOG": True,
    "GRACEFUL_SHUTDOWN_TIMEOUT": 15.0,
    "REQUEST_BUFFER_SIZE": 65536,
    "REQUEST_MAX_HEADER_SIZE": 8192,
    "WEBSOCKET_MAX_SIZE": 2**20,
    "WEBSOCKET_PING_INTERVAL": 20,
    "WEBSOCKET_PING_TIMEOUT": 20,
    "NOISY_EXCEPTIONS": False,
}


def _convert_value(value):
    if not isinstance(value, str):
        return value
    low = value.lower()
    if low in _BOOL_STRINGS:
        return _BOOL_STRINGS[low]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


class AppConfig(dict):
    def __init__(self, defaults=None, env_prefix=None, **kwargs):
        super().__init__()
        self._env_prefix = env_prefix if env_prefix is not None else "SANIC_"
        self.update(_DEFAULTS)
        if defaults:
            self.update(defaults)
        if kwargs:
            self.update(kwargs)
        self.load_env_vars()

    def __getattr__(self, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"Config has no '{name}' setting")

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self[name] = value

    def load_env_vars(self, prefix=None):
        prefix = prefix or self._env_prefix
        if not prefix:
            return
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):]
                if config_key:
                    self[config_key] = _convert_value(value)

    def update_from_object(self, obj):
        for attr in dir(obj):
            if attr.isupper():
                self[attr] = getattr(obj, attr)

    def update_config(self, config):
        if isinstance(config, dict):
            self.update(config)
        elif isinstance(config, str):
            self._load_from_file(config)
        elif hasattr(config, "__dict__"):
            self.update_from_object(config)

    def _load_from_file(self, filepath):
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", filepath)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.update_from_object(module)
