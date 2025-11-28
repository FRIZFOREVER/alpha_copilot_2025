import pytest
from fastapi import FastAPI

from ml.api import app as create_app


@pytest.fixture()
def fastapi_app() -> FastAPI:
    return create_app()


def test_health_route(fastapi_app: FastAPI) -> None:
    assert str(fastapi_app.url_path_for("message_stream")) == "/message_stream"
