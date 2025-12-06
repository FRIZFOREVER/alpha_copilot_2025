import json
import sys
from pathlib import Path
from typing import Awaitable, Callable

import httpx
import pytest

sys.path.append(str(Path(__file__).resolve().parents[2]))

from integration.todoist_service import TodoistService


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("TELEGRAM_DATA_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def service(data_dir: Path) -> TodoistService:
    return TodoistService()


def patch_async_client(
    monkeypatch: pytest.MonkeyPatch, handler: Callable[[httpx.Request], Awaitable[httpx.Response]]
) -> None:
    transport = httpx.MockTransport(handler)
    original_async_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)


def prepare_authorized_service(service: TodoistService, user_id: str = "user1") -> str:
    token = "test-token"
    service.save_todoist_token(user_id, token)
    return token


@pytest.mark.anyio
async def test_create_task_success(monkeypatch: pytest.MonkeyPatch, service: TodoistService) -> None:
    token = prepare_authorized_service(service)

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("Authorization") == f"Bearer {token}"
        body = json.loads(request.content)
        assert body["content"] == "Buy milk"
        return httpx.Response(
            200,
            json={"id": "123", "content": "Buy milk", "url": "https://todoist.com/task"},
        )

    patch_async_client(monkeypatch, handler)

    result = await service.create_task("user1", "Buy milk")

    assert result == {
        "success": True,
        "task_id": "123",
        "content": "Buy milk",
        "url": "https://todoist.com/task",
        "message": "Task created in Todoist",
    }


@pytest.mark.anyio
async def test_create_task_timeout(monkeypatch: pytest.MonkeyPatch, service: TodoistService) -> None:
    prepare_authorized_service(service)

    async def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover - raised
        raise httpx.TimeoutException("request timed out")

    patch_async_client(monkeypatch, handler)

    result = await service.create_task("user1", "Buy bread")

    assert result["success"] is False
    assert result["error"].startswith("Failed to create task: request timed out")


@pytest.mark.anyio
async def test_create_task_non_200(monkeypatch: pytest.MonkeyPatch, service: TodoistService) -> None:
    prepare_authorized_service(service)

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="internal failure")

    patch_async_client(monkeypatch, handler)

    result = await service.create_task("user1", "Buy apples")

    assert result == {
        "success": False,
        "error": "Todoist API error: 500 - internal failure",
    }


@pytest.mark.anyio
async def test_get_projects_success(monkeypatch: pytest.MonkeyPatch, service: TodoistService) -> None:
    prepare_authorized_service(service)

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"id": "p1", "name": "Home"}])

    patch_async_client(monkeypatch, handler)

    result = await service.get_projects("user1")

    assert result == {"status": "ok", "projects": [{"id": "p1", "name": "Home"}]}


@pytest.mark.anyio
async def test_get_projects_timeout(monkeypatch: pytest.MonkeyPatch, service: TodoistService) -> None:
    prepare_authorized_service(service)

    async def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover - raised
        raise httpx.TimeoutException("slow network")

    patch_async_client(monkeypatch, handler)

    result = await service.get_projects("user1")

    assert result["status"] == "error"
    assert result["projects"] == []
    assert "slow network" in result["error"]


@pytest.mark.anyio
async def test_get_projects_non_200(monkeypatch: pytest.MonkeyPatch, service: TodoistService) -> None:
    prepare_authorized_service(service)

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="forbidden")

    patch_async_client(monkeypatch, handler)

    result = await service.get_projects("user1")

    assert result == {
        "status": "error",
        "error": "Failed to get projects: 403",
        "projects": [],
    }
