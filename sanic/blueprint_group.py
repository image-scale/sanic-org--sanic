"""Blueprint group."""
from typing import Any, Iterable, List, Optional, Sequence, Union


class BlueprintGroup(list):
    """Group of blueprints."""

    __slots__ = (
        "_url_prefix",
        "_version",
        "_strict_slashes",
        "_version_prefix",
    )

    def __init__(
        self,
        url_prefix: Optional[str] = None,
        version: Optional[Union[int, str, float]] = None,
        strict_slashes: Optional[bool] = None,
        version_prefix: str = "/v",
        blueprints: Sequence = (),
    ):
        super().__init__(blueprints)
        self._url_prefix = url_prefix
        self._version = version
        self._strict_slashes = strict_slashes
        self._version_prefix = version_prefix

    @property
    def url_prefix(self) -> Optional[str]:
        return self._url_prefix

    @property
    def blueprints(self) -> List:
        return list(self)

    @property
    def version(self) -> Optional[Union[int, str, float]]:
        return self._version

    @property
    def strict_slashes(self) -> Optional[bool]:
        return self._strict_slashes

    @property
    def version_prefix(self) -> str:
        return self._version_prefix

    def append(self, value) -> None:
        """Add blueprint to group."""
        super().append(value)

    def insert(self, index: int, value) -> None:
        """Insert blueprint at index."""
        super().insert(index, value)

    def extend(self, values: Iterable) -> None:
        """Extend group with blueprints."""
        super().extend(values)

    def middleware(self, *args, **kwargs):
        """Register middleware on all blueprints."""
        def decorator(handler):
            for bp in self:
                bp.middleware(*args, **kwargs)(handler)
            return handler
        return decorator

    def on_request(self, middleware=None):
        """Register request middleware on all blueprints."""
        return self.middleware(middleware, "request")

    def on_response(self, middleware=None):
        """Register response middleware on all blueprints."""
        return self.middleware(middleware, "response")
