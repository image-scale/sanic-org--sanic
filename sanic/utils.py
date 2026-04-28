"""Sanic utility functions."""
import asyncio
import importlib.util
import sys

from functools import partial
from pathlib import Path
from typing import Any, Callable, Coroutine


def str_to_bool(val: str) -> bool:
    """Convert string to boolean."""
    val = val.lower()
    if val in {
        "y",
        "yes",
        "yep",
        "yup",
        "t",
        "true",
        "on",
        "enable",
        "enabled",
        "1",
    }:
        return True
    elif val in {
        "n",
        "no",
        "f",
        "nope",
        "false",
        "off",
        "disable",
        "disabled",
        "0",
    }:
        return False
    else:
        raise ValueError(f"Invalid truth value {val}")


def sanic_endpoint_test(app, method="get", uri="/", gather_request=True, **kwargs):
    """Test endpoint helper."""
    raise NotImplementedError


def load_module_from_file_location(location: str, encoding: str = "utf-8"):
    """Load module from file location."""
    path = Path(location)
    if not path.exists():
        raise ValueError(f"File {location} does not exist")

    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load module from {location}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


__all__ = [
    "load_module_from_file_location",
    "str_to_bool",
    "sanic_endpoint_test",
]
