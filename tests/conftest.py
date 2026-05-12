import pytest
from sanic import Sanic
from sanic.test_utils import AppTestClient


@pytest.fixture
def app():
    inst = Sanic("test_app")
    yield inst
    Sanic._registry.pop("test_app", None)


@pytest.fixture
def client(app):
    return AppTestClient(app)
