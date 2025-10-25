from fastapi.testclient import TestClient

from ml.api.app import create_app


def test_ping_endpoint_returns_expected_payload() -> None:
    client = TestClient(create_app())

    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_health_endpoint_reports_healthy_status() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_react_endpoint_returns_workflow_message() -> None:
    client = TestClient(create_app())

    response = client.get("/react")

    assert response.status_code == 200
    assert response.json() == {"message": "react workflow"}
