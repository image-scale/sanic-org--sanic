import asyncio
import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient
from sanic.response_types import make_json, make_text
from sanic.signals import SignalDispatcher, LifecycleEvent


class TestSignalDispatcher:
    def test_register_and_dispatch(self):
        dispatcher = SignalDispatcher()
        results = []

        async def handler(**kwargs):
            results.append("fired")

        dispatcher.register("test.event", handler)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(dispatcher.dispatch("test.event"))
        loop.close()

        assert results == ["fired"]

    def test_dispatch_with_kwargs(self):
        dispatcher = SignalDispatcher()
        captured = {}

        async def handler(**kwargs):
            captured.update(kwargs)

        dispatcher.register("test.event", handler)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            dispatcher.dispatch("test.event", data="hello")
        )
        loop.close()

        assert captured == {"data": "hello"}

    def test_multiple_handlers_for_same_event(self):
        dispatcher = SignalDispatcher()
        order = []

        async def handler_a(**kwargs):
            order.append("a")

        async def handler_b(**kwargs):
            order.append("b")

        dispatcher.register("test.event", handler_a)
        dispatcher.register("test.event", handler_b)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(dispatcher.dispatch("test.event"))
        loop.close()

        assert "a" in order
        assert "b" in order

    def test_has_handlers(self):
        dispatcher = SignalDispatcher()

        async def handler(**kwargs):
            pass

        assert not dispatcher.has_handlers("test.event")
        dispatcher.register("test.event", handler)
        assert dispatcher.has_handlers("test.event")

    def test_dispatch_nonexistent_event(self):
        dispatcher = SignalDispatcher()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(dispatcher.dispatch("nonexistent"))
        loop.close()


class TestLifecycleEvents:
    def test_lifecycle_event_constants(self):
        assert LifecycleEvent.BEFORE_SERVER_START == "server.init.before"
        assert LifecycleEvent.AFTER_SERVER_START == "server.init.after"
        assert LifecycleEvent.BEFORE_SERVER_STOP == "server.shutdown.before"
        assert LifecycleEvent.AFTER_SERVER_STOP == "server.shutdown.after"


class TestAppListeners:
    def test_before_server_start_decorator(self):
        app = Sanic("listener_test_1")
        events = []

        @app.before_server_start
        async def on_start(app_ref, loop=None):
            events.append("started")

        assert LifecycleEvent.BEFORE_SERVER_START in app.listeners
        assert len(app.listeners[LifecycleEvent.BEFORE_SERVER_START]) == 1
        Sanic._registry.pop("listener_test_1", None)

    def test_after_server_start_decorator(self):
        app = Sanic("listener_test_2")
        events = []

        @app.after_server_start
        async def on_after_start(app_ref, loop=None):
            events.append("after_started")

        assert LifecycleEvent.AFTER_SERVER_START in app.listeners
        Sanic._registry.pop("listener_test_2", None)

    def test_before_server_stop_decorator(self):
        app = Sanic("listener_test_3")

        @app.before_server_stop
        async def on_stop(app_ref, loop=None):
            pass

        assert LifecycleEvent.BEFORE_SERVER_STOP in app.listeners
        Sanic._registry.pop("listener_test_3", None)

    def test_after_server_stop_decorator(self):
        app = Sanic("listener_test_4")

        @app.after_server_stop
        async def on_after_stop(app_ref, loop=None):
            pass

        assert LifecycleEvent.AFTER_SERVER_STOP in app.listeners
        Sanic._registry.pop("listener_test_4", None)

    def test_listener_with_event_string(self):
        app = Sanic("listener_test_5")
        events = []

        @app.listener("server.init.before")
        async def on_start(app_ref, loop=None):
            events.append("started")

        assert "server.init.before" in app.listeners
        Sanic._registry.pop("listener_test_5", None)


class TestCustomSignals:
    def test_register_custom_signal(self):
        app = Sanic("signal_test_1")
        results = []

        @app.signal("my.custom.event")
        async def handler(**kwargs):
            results.append("custom_fired")

        assert app.signal_router.has_handlers("my.custom.event")
        Sanic._registry.pop("signal_test_1", None)

    def test_dispatch_custom_signal(self):
        app = Sanic("signal_test_2")
        results = []

        @app.signal("my.custom.event")
        async def handler(**kwargs):
            results.append(kwargs.get("data", "no_data"))

        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            app.dispatch_signal("my.custom.event", data="hello")
        )
        loop.close()

        assert results == ["hello"]
        Sanic._registry.pop("signal_test_2", None)

    def test_multiple_signal_handlers(self):
        app = Sanic("signal_test_3")
        order = []

        @app.signal("event.x")
        async def first(**kwargs):
            order.append("first")

        @app.signal("event.x")
        async def second(**kwargs):
            order.append("second")

        loop = asyncio.new_event_loop()
        loop.run_until_complete(app.dispatch_signal("event.x"))
        loop.close()

        assert len(order) == 2
        assert "first" in order
        assert "second" in order
        Sanic._registry.pop("signal_test_3", None)


class TestSignalDispatchFromHandler:
    def test_dispatch_signal_in_route_handler(self, app, client):
        events_fired = []

        @app.signal("user.created")
        async def on_user_created(**kwargs):
            events_fired.append(kwargs.get("user_id"))

        @app.post("/users")
        async def create_user(request):
            await app.dispatch_signal("user.created", user_id=42)
            return make_json({"id": 42}, status=201)

        resp = client.post("/users")
        assert resp.status == 201
        assert events_fired == [42]
