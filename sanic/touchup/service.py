"""TouchUp service."""
from typing import Any, List, Set, Tuple


class TouchUp:
    """TouchUp optimization service."""

    _registry: List[Tuple[Any, str]] = []

    @classmethod
    def run(cls, app: Any, optimizations: Set[str] = None):
        """Run touchup optimizations."""
        pass

    @classmethod
    def register(cls, target: Any, method_name: str):
        """Register a method for touchup."""
        cls._registry.append((target, method_name))
