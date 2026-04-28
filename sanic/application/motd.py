"""Message of the Day (MOTD) display."""


class MOTD:
    """MOTD display class."""

    def __init__(self, *args, **kwargs):
        pass

    def display(self):
        """Display MOTD."""
        pass


class MOTDBasic(MOTD):
    """Basic MOTD display."""

    pass


class MOTDTTY(MOTD):
    """TTY MOTD display with colors."""

    pass


__all__ = [
    "MOTD",
    "MOTDBasic",
    "MOTDTTY",
]
