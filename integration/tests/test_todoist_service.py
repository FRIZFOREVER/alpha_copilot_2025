import sys
from datetime import date
from pathlib import Path
from typing import Any

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from integration.todoist_service import TODOIST_API_BASE, TodoistService


class DummyResponse:
    def __init__(self, status_code: int, json_data: dict[str, Any] | None = None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self) -> dict[str, Any]:
        return self._json_data


def patch_async_client(
    monkeypatch: pytest.MonkeyPatch,
    response: DummyResponse,
    requests_log: list[dict[str, Any]],
) -> None:
    class DummyAsyncClient:
        def __init__(self, *_: Any, **__: Any) -> None:
            pass

        async def __aenter__(self) -> "DummyAsyncClient":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

        async def post(
            self,
            url: str,
            headers: dict[str, str] | None = None,
            json: dict[str, Any] | None = None,
            timeout: float | None = None,
        ) -> DummyResponse:
            requests_log.append(
                {
                    "url": url,
                    "headers": headers,
                    "json": json,
                    "timeout": timeout,
                }
            )
            return response

    monkeypatch.setattr("integration.todoist_service.httpx.AsyncClient", DummyAsyncClient)


def patch_fixed_date(monkeypatch: pytest.MonkeyPatch, fixed_date: date) -> None:
    class FixedDate(date):
        @classmethod
        def today(cls) -> "FixedDate":
            return cls(fixed_date.year, fixed_date.month, fixed_date.day)

    monkeypatch.setattr("integration.todoist_service.date", FixedDate)


def patch_auth_data(monkeypatch: pytest.MonkeyPatch, token: str) -> None:
    monkeypatch.setattr(
        TodoistService,
        "_load_auth_data",
        lambda self: {"user-1": {"token": token, "authorized": True}},
    )


@pytest.mark.anyio("asyncio")
async def test_create_task_sends_optional_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    fixed_date = date(2024, 2, 3)
    patch_fixed_date(monkeypatch, fixed_date)
    patch_auth_data(monkeypatch, "token-123")

    requests_log: list[dict[str, Any]] = []
    response = DummyResponse(
        200,
        json_data={"id": "task-1", "content": "do it", "url": "https://todoist"},
    )
    patch_async_client(monkeypatch, response, requests_log)

    service = TodoistService()
    result = await service.create_task(
        "user-1", "do it", description="details", labels=["home", "work"]
    )

    assert result["success"] is True
    assert result["task_id"] == "task-1"

    assert requests_log == [
        {
            "url": f"{TODOIST_API_BASE}/tasks",
            "headers": {
                "Authorization": "Bearer token-123",
                "Content-Type": "application/json",
            },
            "json": {
                "content": "do it",
                "priority": 3,
                "due_date": fixed_date.isoformat(),
                "description": "details",
                "labels": ["home", "work"],
            },
            "timeout": 30.0,
        }
    ]


@pytest.mark.anyio("asyncio")
async def test_create_task_omits_empty_optional_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    fixed_date = date(2024, 5, 6)
    patch_fixed_date(monkeypatch, fixed_date)
    patch_auth_data(monkeypatch, "token-abc")

    requests_log: list[dict[str, Any]] = []
    response = DummyResponse(
        200,
        json_data={"id": "task-2", "content": "plan", "url": "https://todoist/task"},
    )
    patch_async_client(monkeypatch, response, requests_log)

    service = TodoistService()
    result = await service.create_task("user-1", "plan")

    assert result["success"] is True

    assert requests_log[0]["json"] == {
        "content": "plan",
        "priority": 3,
        "due_date": fixed_date.isoformat(),
    }


@pytest.mark.anyio("asyncio")
async def test_create_task_returns_error_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_auth_data(monkeypatch, "token-exc")

    class RaisingAsyncClient:
        def __init__(self, *_: Any, **__: Any) -> None:
            pass

        async def __aenter__(self) -> "RaisingAsyncClient":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

        async def post(self, *_: Any, **__: Any) -> DummyResponse:
            raise RuntimeError("boom")

    monkeypatch.setattr("integration.todoist_service.httpx.AsyncClient", RaisingAsyncClient)

    service = TodoistService()
    result = await service.create_task("user-1", "fail")

    assert result["success"] is False
    assert "boom" in result["error"]
