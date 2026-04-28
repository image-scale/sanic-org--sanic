"""Request form handling."""
from typing import Optional


class File:
    """Uploaded file."""

    __slots__ = ("type", "body", "name")

    def __init__(
        self,
        type: Optional[str] = None,
        body: Optional[bytes] = None,
        name: Optional[str] = None,
    ):
        self.type = type
        self.body = body
        self.name = name

    def __repr__(self):
        return f"File(type={self.type!r}, name={self.name!r})"
