"""TLS certificate creators."""
import ssl
from typing import Any, Optional


class MkcertCreator:
    """Create certificates with mkcert."""

    def __init__(self, app, key, cert):
        self.app = app
        self.key = key
        self.cert = cert

    def generate_cert(self, hostname: str):
        """Generate certificate."""
        pass


class TrustmeCreator:
    """Create certificates with trustme."""

    def __init__(self, app, key, cert):
        self.app = app
        self.key = key
        self.cert = cert

    def generate_cert(self, hostname: str):
        """Generate certificate."""
        pass


def get_ssl_context(
    ssl_context: Optional[ssl.SSLContext] = None,
    certfile: Optional[str] = None,
    keyfile: Optional[str] = None,
    password: Optional[str] = None,
) -> ssl.SSLContext:
    """Get SSL context."""
    if ssl_context:
        return ssl_context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    if certfile:
        context.load_cert_chain(certfile, keyfile, password)
    return context


__all__ = [
    "MkcertCreator",
    "TrustmeCreator",
    "get_ssl_context",
]
