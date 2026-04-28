"""Deprecation warnings."""
import warnings


def deprecation(message: str, version: str):
    """Issue deprecation warning."""
    warnings.warn(
        f"{message} This will be removed in version {version}.",
        DeprecationWarning,
        stacklevel=3,
    )
