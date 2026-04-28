"""Response cookie handling."""
from datetime import datetime
from typing import Any, Dict, List, Optional


class Cookie(dict):
    """HTTP Cookie."""

    _keys = {
        "path",
        "comment",
        "domain",
        "max-age",
        "expires",
        "samesite",
        "version",
        "secure",
        "httponly",
        "partitioned",
    }
    _flags = {"secure", "httponly", "partitioned"}

    def __init__(
        self,
        key: str,
        value: str = "",
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = True,
        httponly: bool = False,
        samesite: Optional[str] = "Lax",
        max_age: Optional[int] = None,
        expires: Optional[datetime] = None,
        comment: Optional[str] = None,
        partitioned: bool = False,
    ):
        super().__init__()
        self.key = key
        self.value = value
        self["path"] = path
        if domain:
            self["domain"] = domain
        self["secure"] = secure
        self["httponly"] = httponly
        if samesite:
            self["samesite"] = samesite
        if max_age is not None:
            self["max-age"] = max_age
        if expires:
            self["expires"] = expires
        if comment:
            self["comment"] = comment
        self["partitioned"] = partitioned

    def __str__(self) -> str:
        return self.encode()

    def encode(self) -> str:
        """Encode cookie to string."""
        output = [f"{self.key}={self.value}"]
        for key in self._keys:
            if key in self:
                value = self[key]
                if key in self._flags:
                    if value:
                        output.append(key.capitalize())
                elif value is not None:
                    if isinstance(value, datetime):
                        value = value.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
                    output.append(f"{key}={value}")
        return "; ".join(output)


class CookieJar(dict):
    """Collection of cookies for response."""

    def __init__(self, headers: Any = None):
        super().__init__()
        self._headers = headers

    def add_cookie(
        self,
        key: str,
        value: str = "",
        **kwargs,
    ) -> Cookie:
        """Add a cookie."""
        cookie = Cookie(key, value, **kwargs)
        self[key] = cookie
        return cookie

    def delete_cookie(
        self,
        key: str,
        path: str = "/",
        domain: Optional[str] = None,
    ):
        """Delete a cookie."""
        self[key] = Cookie(
            key,
            "",
            path=path,
            domain=domain,
            max_age=0,
        )

    @property
    def header_output(self) -> List[str]:
        """Get header output."""
        return [cookie.encode() for cookie in self.values()]

    def __setitem__(self, key: str, value):
        if isinstance(value, Cookie):
            super().__setitem__(key, value)
        else:
            super().__setitem__(key, Cookie(key, value))
