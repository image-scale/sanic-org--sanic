"""Sanic headers module."""
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union


def parse_accept(accept_str: str) -> List["MediaType"]:
    """Parse Accept header."""
    result = []
    if not accept_str:
        return result
    for part in accept_str.split(","):
        part = part.strip()
        if part:
            result.append(MediaType.parse(part))
    result.sort(key=lambda x: x.q, reverse=True)
    return result


class Matched:
    """Matched media type."""

    def __init__(self, mime: str, header: "MediaType"):
        self.mime = mime
        self.header = header

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.mime == other
        return self.mime == other.mime


class MediaType:
    """Media type representation."""

    def __init__(
        self,
        type_: str,
        subtype: str,
        q: float = 1.0,
        params: Optional[Dict[str, str]] = None,
    ):
        self.type = type_
        self.subtype = subtype
        self.q = q
        self.params = params or {}
        self.mime = f"{type_}/{subtype}"

    @classmethod
    def parse(cls, media_str: str) -> "MediaType":
        """Parse media type string."""
        parts = media_str.split(";")
        mime = parts[0].strip()
        type_, subtype = mime.split("/") if "/" in mime else (mime, "*")

        q = 1.0
        params = {}
        for param in parts[1:]:
            param = param.strip()
            if "=" in param:
                key, value = param.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == "q":
                    q = float(value)
                else:
                    params[key] = value

        return cls(type_, subtype, q, params)

    def __str__(self) -> str:
        result = self.mime
        if self.params:
            for k, v in self.params.items():
                result += f";{k}={v}"
        if self.q != 1.0:
            result += f";q={self.q}"
        return result


class AcceptList(list):
    """List of accepted media types."""

    def __init__(self, accept_str: str = ""):
        super().__init__()
        self._accept_str = accept_str
        self.extend(parse_accept(accept_str))

    def __str__(self) -> str:
        return self._accept_str

    def match(self, *choices) -> Optional[Matched]:
        """Match against choices."""
        for header in self:
            for choice in choices:
                if self._matches(header, choice):
                    return Matched(choice, header)
        return None

    def _matches(self, header: MediaType, choice: str) -> bool:
        """Check if header matches choice."""
        if "/" in choice:
            c_type, c_subtype = choice.split("/", 1)
            # Strip parameters from choice
            if ";" in c_subtype:
                c_subtype = c_subtype.split(";")[0]
        else:
            return False

        if header.type == "*" or c_type == "*":
            return True
        if header.type != c_type:
            return False
        if header.subtype == "*" or c_subtype == "*":
            return True
        return header.subtype == c_subtype


def format_http1_response(status: int, headers: Iterable[Tuple[str, str]]) -> bytes:
    """Format HTTP/1 response headers."""
    raise NotImplementedError


def format_http1(headers: Iterable[Tuple[str, str]]) -> bytes:
    """Format HTTP/1 headers."""
    raise NotImplementedError


__all__ = [
    "AcceptList",
    "MediaType",
    "Matched",
    "parse_accept",
    "format_http1_response",
    "format_http1",
]
