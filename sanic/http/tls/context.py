"""TLS context."""
import ssl
from typing import Any, Optional


class CertSimple:
    """Simple certificate configuration."""

    def __init__(self, cert: str, key: str, password: Optional[str] = None):
        self.cert = cert
        self.key = key
        self.password = password


class CertSelector:
    """Certificate selector."""

    pass


class SanicSSLContext(ssl.SSLContext):
    """Sanic SSL context."""

    pass


__all__ = [
    "CertSelector",
    "CertSimple",
    "SanicSSLContext",
]
