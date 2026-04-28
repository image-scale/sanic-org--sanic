"""Goodbye message."""


GOODBYE_MESSAGES = [
    "Goodbye!",
    "Shutting down...",
    "See you next time!",
]


def choose_goodbye_message() -> str:
    """Choose a goodbye message."""
    return GOODBYE_MESSAGES[0]
