"""Base Sanic class."""
import re

from typing import TYPE_CHECKING, Any, Optional, Set

from sanic.base.meta import SanicMeta


NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")


class BaseSanic(metaclass=SanicMeta):
    """Base class for Sanic and Blueprint."""

    __slots__ = (
        "_name",
        "ctx",
    )

    name: str

    def __init__(self, name: str = None, *args, **kwargs):
        from sanic.exceptions import SanicException

        class_name = self.__class__.__name__
        if name is None:
            raise TypeError(
                f"Missing required argument 'name'. "
                f"Example: {class_name}(name='my_{class_name.lower()}')"
            )

        if not NAME_PATTERN.match(name):
            raise SanicException(
                f"{class_name} instance named '{name}' uses an invalid format. "
                "Names must begin with a character and may only contain "
                "alphanumeric characters, _, or -."
            )

        self._name = name
        self.ctx = SimpleNamespace()

    @property
    def name(self) -> str:
        return self._name


class SimpleNamespace:
    """Simple namespace for ctx."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"Namespace({self.__dict__})"
