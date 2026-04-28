"""App loader."""
import os
import sys

from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Optional, Union

from sanic.http.tls.creators import MkcertCreator, TrustmeCreator


class AppLoader:
    """Application loader."""

    def __init__(
        self,
        module_input: Optional[str] = None,
        as_factory: bool = False,
        as_simple: bool = False,
        args: Optional[SimpleNamespace] = None,
        factory: Optional[Callable] = None,
    ):
        self.module_input = module_input
        self.as_factory = as_factory
        self.as_simple = as_simple
        self.args = args
        self.factory = factory

    def load(self) -> "Sanic":
        """Load the application."""
        from sanic.app import Sanic

        # Add cwd to path
        cwd = os.getcwd()
        if cwd not in sys.path:
            sys.path.insert(0, cwd)

        if self.factory:
            return self.factory()

        if self.module_input is None:
            raise ValueError("No module input provided")

        # Check if it's a directory (simple mode)
        if os.path.isdir(self.module_input):
            return Sanic("SimpleServer")

        # Handle module:attribute format
        if ":" in self.module_input:
            module_path, attr = self.module_input.split(":", 1)
            # Remove () if present for factory
            attr = attr.rstrip("()")
        else:
            # Try to interpret as module.attr or just module
            parts = self.module_input.rsplit(".", 1)
            if len(parts) == 2:
                module_path, attr = parts
            else:
                module_path = self.module_input
                attr = "app"

        # Import the module
        import importlib

        module = importlib.import_module(module_path)

        # Get the attribute
        app_or_factory = getattr(module, attr)

        # If it's a factory, call it
        if self.as_factory or callable(app_or_factory) and not isinstance(
            app_or_factory, Sanic
        ):
            # Check if the factory needs arguments
            if self.args and hasattr(self.args, "target"):
                return app_or_factory()
            return app_or_factory()

        return app_or_factory


class CertLoader:
    """Certificate loader."""

    _creators = {
        "mkcert": MkcertCreator,
        "trustme": TrustmeCreator,
    }

    def __init__(self, data: dict):
        self.data = data
        self.creator_name = data.get("creator", "mkcert")

    def load(self, app: Any):
        """Load certificates."""
        creator_class = self._creators.get(self.creator_name)
        if creator_class:
            creator = creator_class(
                app,
                self.data.get("key"),
                self.data.get("cert"),
            )
            creator.generate_cert(self.data.get("localhost", "localhost"))
