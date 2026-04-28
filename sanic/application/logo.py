"""Sanic logo utilities."""

SANIC_LOGO = """\
                 Sanic
         Build Fast. Run Fast.
"""

BASE_LOGO = """

                 Sanic
         Build Fast. Run Fast.

"""

COLOR_LOGO = """\
                 \033[38;2;255;13;104mSanic\033[0m
         Build Fast. Run Fast.
"""

FULL_COLOR_LOGO = """\
\033[38;2;255;13;104m                 Sanic\033[0m
         Build Fast. Run Fast.
"""

COFFEE_LOGO = """
        ( (
          ) )
       ........
       |      |]
       \\      /
        `----'
      ☕ Coffee Mode
"""


def get_logo(full: bool = False) -> str:
    """Get Sanic logo."""
    return BASE_LOGO if full else SANIC_LOGO


__all__ = [
    "BASE_LOGO",
    "COFFEE_LOGO",
    "COLOR_LOGO",
    "FULL_COLOR_LOGO",
    "SANIC_LOGO",
    "get_logo",
]
