"""Logger instances."""
import logging


logger = logging.getLogger("sanic.root")
error_logger = logging.getLogger("sanic.error")
access_logger = logging.getLogger("sanic.access")
server_logger = logging.getLogger("sanic.server")
