"""Base page."""


class BasePage:
    """Base page class."""

    def __init__(self, *args, **kwargs):
        pass

    def render(self) -> str:
        """Render page to HTML."""
        raise NotImplementedError
