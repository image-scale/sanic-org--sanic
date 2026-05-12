import asyncio
from collections import defaultdict


class LifecycleEvent:
    BEFORE_SERVER_START = "server.init.before"
    AFTER_SERVER_START = "server.init.after"
    BEFORE_SERVER_STOP = "server.shutdown.before"
    AFTER_SERVER_STOP = "server.shutdown.after"


class SignalDispatcher:
    def __init__(self):
        self._handlers = defaultdict(list)

    def register(self, event_name, handler, *, priority=0):
        self._handlers[event_name].append((priority, handler))
        self._handlers[event_name].sort(key=lambda e: -e[0])

    def get_handlers(self, event_name):
        return [h for _, h in self._handlers[event_name]]

    async def dispatch(self, event_name, **kwargs):
        for _, handler in self._handlers.get(event_name, []):
            result = handler(**kwargs)
            if asyncio.iscoroutine(result):
                await result

    def has_handlers(self, event_name):
        return len(self._handlers.get(event_name, [])) > 0
