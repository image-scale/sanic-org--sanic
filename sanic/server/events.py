"""Server events."""
from typing import Callable, List


def trigger_events(events: List[Callable], loop, **kwargs):
    """Trigger server events."""
    raise NotImplementedError
