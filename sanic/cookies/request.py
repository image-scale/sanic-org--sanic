"""Request cookie handling."""
from typing import Dict


def parse_cookie(cookie_string: str) -> Dict[str, str]:
    """Parse cookie string into dict."""
    cookies = {}
    if cookie_string:
        for item in cookie_string.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()
    return cookies


class CookieRequestParameters(dict):
    """Request cookie parameters."""

    def __init__(self, cookies: str = ""):
        super().__init__()
        if cookies:
            self._parse(cookies)

    def _parse(self, cookies: str):
        """Parse cookie string."""
        for item in cookies.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                self[key.strip()] = value.strip()

    def getlist(self, key: str):
        """Get cookie value as list."""
        value = self.get(key)
        if value is None:
            return []
        return [value]


__all__ = [
    "CookieRequestParameters",
    "parse_cookie",
]
