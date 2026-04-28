"""Sanic configuration."""
from __future__ import annotations

import os

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from sanic.constants import LocalCertCreator
from sanic.exceptions import PyFileError


# Default configuration values
DEFAULT_CONFIG = {
    "ACCESS_LOG": False,
    "AUTO_EXTEND": True,
    "AUTO_RELOAD": False,
    "EVENT_AUTOREGISTER": True,
    "FALLBACK_ERROR_FORMAT": "auto",
    "FORWARDED_FOR_HEADER": "X-Forwarded-For",
    "FORWARDED_SECRET": None,
    "GRACEFUL_SHUTDOWN_TIMEOUT": 15.0,
    "INSPECTOR": False,
    "INSPECTOR_HOST": "localhost",
    "INSPECTOR_PORT": 6457,
    "INSPECTOR_TLS_KEY": None,
    "INSPECTOR_TLS_CERT": None,
    "INSPECTOR_API_KEY": None,
    "KEEP_ALIVE": True,
    "KEEP_ALIVE_TIMEOUT": 120,
    "LOCAL_CERT_CREATOR": LocalCertCreator.AUTO,
    "LOCAL_TLS_KEY": None,
    "LOCAL_TLS_CERT": None,
    "LOCALHOST": "localhost",
    "MOTD": True,
    "MOTD_DISPLAY": {},
    "NOISY_EXCEPTIONS": False,
    "PROXIES_COUNT": None,
    "REAL_IP_HEADER": None,
    "REQUEST_BUFFER_SIZE": 65536,
    "REQUEST_ID_HEADER": "X-Request-ID",
    "REQUEST_MAX_HEADER_SIZE": 8192,
    "REQUEST_MAX_SIZE": 100000000,
    "REQUEST_TIMEOUT": 60,
    "RESPONSE_TIMEOUT": 60,
    "TOUCHUP": True,
    "USE_UVLOOP": True,
    "WEBSOCKET_MAX_SIZE": 2**20,
    "WEBSOCKET_PING_INTERVAL": 20,
    "WEBSOCKET_PING_TIMEOUT": 20,
}


class DetailedConverter(ABC):
    """Base class for converters that need access to all conversion parameters."""

    @abstractmethod
    def __call__(
        self, full_key: str, config_key: str, value: str, defaults: dict
    ) -> Any:
        """Convert a value with access to all conversion context."""
        ...


def _convert_value(value: str, converters: List[Callable]) -> Any:
    """Convert string value to appropriate type."""
    # Try each converter in order
    for converter in converters:
        try:
            return converter(value)
        except (ValueError, TypeError):
            continue

    return value


def _convert_to_local_cert_creator(value: str) -> LocalCertCreator:
    """Convert string to LocalCertCreator enum."""
    return LocalCertCreator[value.upper()]


class Config(dict):
    """Sanic configuration object."""

    _converters: List[Callable] = [
        int,
        float,
        lambda x: x.lower() in ("true", "yes", "1"),
        _convert_to_local_cert_creator,
        str,
    ]

    def __init__(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        env_prefix: Optional[str] = "SANIC_",
        keep_alive: Optional[bool] = None,
        converters: Optional[Sequence[Callable]] = None,
    ):
        super().__init__()
        self._env_prefix = env_prefix if env_prefix is not None else "SANIC_"
        self._defaults = {**DEFAULT_CONFIG, **(defaults or {})}

        if converters:
            self._converters = list(converters) + self._converters

        # Load defaults
        for key, value in self._defaults.items():
            super().__setitem__(key, value)

        # Override with environment variables
        if self._env_prefix:
            self._load_from_env()

        # Override keep_alive if explicitly set
        if keep_alive is not None:
            self["KEEP_ALIVE"] = keep_alive

    def _load_from_env(self):
        """Load configuration from environment variables."""
        for key, value in os.environ.items():
            if self._env_prefix and key.startswith(self._env_prefix):
                config_key = key[len(self._env_prefix):]
                if config_key.isupper():
                    converted = self._convert_env_value(key, config_key, value)
                    super().__setitem__(config_key, converted)

    def _convert_env_value(self, full_key: str, config_key: str, value: str) -> Any:
        """Convert environment variable value."""
        for converter in self._converters:
            try:
                if isinstance(converter, type) and issubclass(converter, DetailedConverter):
                    return converter()(full_key, config_key, value, self._defaults)
                elif isinstance(converter, DetailedConverter):
                    return converter(full_key, config_key, value, self._defaults)
                result = converter(value)
                if result is not None:
                    return result
            except (ValueError, TypeError, KeyError):
                continue
        return value

    def load(self, source: Any):
        """Load configuration from various sources."""
        if isinstance(source, str):
            if source.startswith("${") and source.endswith("}"):
                # Environment variable reference
                env_var = source[2:-1]
                source = os.environ.get(env_var)
                if not source:
                    raise IOError(f"Environment variable '{env_var}' not found")

            # Check if it's a module path or file path
            if os.path.isfile(source):
                self._load_from_file(source)
            elif "." in source:
                self._load_from_module(source)
            else:
                raise IOError(f"Configuration file not found: {source}")
        elif isinstance(source, type):
            self._load_from_class(source)
        elif isinstance(source, dict):
            self._load_from_dict(source)
        else:
            self._load_from_object(source)

    def _load_from_file(self, path: str):
        """Load configuration from Python file."""
        import types

        path = Path(path)
        try:
            module = types.ModuleType("config")
            module.__file__ = str(path)
            with open(path) as f:
                exec(compile(f.read(), path, "exec"), module.__dict__)

            for key in dir(module):
                if key.isupper():
                    self[key] = getattr(module, key)
        except Exception as e:
            raise PyFileError(str(path), e)

    def _load_from_module(self, module_path: str):
        """Load configuration from module path."""
        import importlib

        try:
            module = importlib.import_module(module_path)
            self._load_from_class(module)
        except ImportError:
            raise ImportError(f"Unable to import {module_path}")

    def _load_from_class(self, cls):
        """Load configuration from class."""
        for key in dir(cls):
            if key.isupper():
                self[key] = getattr(cls, key)

    def _load_from_object(self, obj):
        """Load configuration from object."""
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def _load_from_dict(self, d: dict):
        """Load configuration from dictionary."""
        for key, value in d.items():
            if key.isupper():
                self[key] = value

    def update_config(self, config: Any):
        """Update configuration from various sources."""
        if isinstance(config, dict):
            for key, value in config.items():
                if key.isupper():
                    self[key] = value
        elif isinstance(config, (str, Path)):
            self.load(str(config))
        else:
            self._load_from_object(config)

    def _post_set(self, key: str, value: Any):
        """Hook called after setting a value."""
        pass

    def __setattr__(self, name: str, value: Any):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self[name] = value

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"Config has no '{name}'")

    def __setitem__(self, key: str, value: Any):
        super().__setitem__(key, value)
        self._post_set(key, value)

    def register_type(self, converter: Callable):
        """Register a type converter."""
        import logging
        if converter in self._converters:
            logging.getLogger("sanic.error").warning(
                f"Configuration value converter '{converter.__name__}' has already been registered"
            )
        else:
            self._converters.insert(0, converter)

    def update(self, *args, **kwargs):
        """Update config values."""
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    self[key] = value
            elif hasattr(arg, "items"):
                for key, value in arg.items():
                    self[key] = value
            else:
                for key, value in arg:
                    self[key] = value

        for key, value in kwargs.items():
            self[key] = value


__all__ = [
    "Config",
    "DEFAULT_CONFIG",
    "DetailedConverter",
]
