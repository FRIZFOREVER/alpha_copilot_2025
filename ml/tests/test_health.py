import asyncio

import pytest
from fastapi import FastAPI

from ml.api import app as create_app
from ml.api.routes import health


@pytest.fixture()
def fastapi_app() -> FastAPI:
    return create_app()


def test_ping_endpoint() -> None:
    response = asyncio.run(health.ping())

    assert response == {"message": "pong"}


def test_health_route(fastapi_app: FastAPI) -> None:
    assert str(fastapi_app.url_path_for("ping")) == "/ping"


def test_app_title(fastapi_app: FastAPI) -> None:
    assert fastapi_app.title == "ml service"
