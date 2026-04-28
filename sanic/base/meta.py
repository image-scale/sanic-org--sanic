"""Sanic metaclass."""
import re

from typing import Set


class SanicMeta(type):
    """Metaclass for Sanic."""

    _class_registry: dict = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace)
        return cls
