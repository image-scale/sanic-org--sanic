"""Logging setup."""
import logging

from sanic.logging.default import LOGGING_CONFIG_DEFAULTS


def setup_logging(debug: bool = False, log_config: dict = None):
    """Setup logging configuration."""
    if log_config is None:
        log_config = LOGGING_CONFIG_DEFAULTS

    logging.config.dictConfig(log_config)
