"""Protocol types."""
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sanic.server.protocols.http_protocol import HttpProtocol
