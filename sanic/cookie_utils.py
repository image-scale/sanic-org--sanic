from datetime import datetime, timezone
from http.cookies import SimpleCookie


def parse_request_cookies(raw_cookie_header):
    result = {}
    if not raw_cookie_header:
        return result
    pairs = raw_cookie_header.split(";")
    for pair in pairs:
        pair = pair.strip()
        if "=" in pair:
            key, _, value = pair.partition("=")
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            if key:
                result[key] = value
    return result


class ResponseCookie:
    def __init__(self, key, value, *, path="/", domain=None, secure=True,
                 httponly=False, samesite="Lax", max_age=None, expires=None,
                 comment=None, host_prefix=False, secure_prefix=False,
                 partitioned=False):
        self.key = key
        self.value = value
        self.path = path
        self.domain = domain
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite
        self.max_age = max_age
        self.expires = expires
        self.comment = comment
        self.host_prefix = host_prefix
        self.secure_prefix = secure_prefix
        self.partitioned = partitioned

        if host_prefix:
            self.secure = True
            self.path = "/"
            self.domain = None
        if secure_prefix:
            self.secure = True

    @property
    def encoded_key(self):
        if self.host_prefix:
            return f"__Host-{self.key}"
        if self.secure_prefix:
            return f"__Secure-{self.key}"
        return self.key

    def to_header(self):
        parts = [f"{self.encoded_key}={self.value}"]
        if self.path:
            parts.append(f"Path={self.path}")
        if self.domain:
            parts.append(f"Domain={self.domain}")
        if self.max_age is not None:
            parts.append(f"Max-Age={self.max_age}")
        if self.expires is not None:
            if isinstance(self.expires, datetime):
                exp_str = self.expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
                parts.append(f"Expires={exp_str}")
            else:
                parts.append(f"Expires={self.expires}")
        if self.secure:
            parts.append("Secure")
        if self.httponly:
            parts.append("HttpOnly")
        if self.samesite:
            parts.append(f"SameSite={self.samesite}")
        if self.partitioned:
            parts.append("Partitioned")
        if self.comment:
            parts.append(f"Comment={self.comment}")
        return "; ".join(parts)


class ResponseCookieJar:
    def __init__(self):
        self._cookies = {}

    def add(self, key, value, **kwargs):
        cookie = ResponseCookie(key, value, **kwargs)
        self._cookies[cookie.encoded_key] = cookie
        return cookie

    def delete(self, key, *, path="/", domain=None, host_prefix=False,
               secure_prefix=False):
        cookie = ResponseCookie(
            key, "",
            path=path, domain=domain,
            max_age=0, host_prefix=host_prefix,
            secure_prefix=secure_prefix,
        )
        self._cookies[cookie.encoded_key] = cookie
        return cookie

    def get(self, key):
        return self._cookies.get(key)

    def has(self, key):
        return key in self._cookies

    def __iter__(self):
        return iter(self._cookies.values())

    def __len__(self):
        return len(self._cookies)

    def header_values(self):
        return [cookie.to_header() for cookie in self._cookies.values()]
