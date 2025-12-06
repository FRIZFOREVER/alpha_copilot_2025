"""Tests for tool registry behavior."""

from typing import Any
import sys
import types

import pytest

dummy_router = types.ModuleType("ml.domain.workflow.router")
dummy_router.workflow = lambda *_, **__: None
dummy_router.workflow_collected = lambda *_, **__: None
sys.modules.setdefault("ml.domain.workflow.router", dummy_router)

from ml.domain.models.tools_data import ToolResult
from ml.domain.workflow.agent.tools.base_tool import BaseTool
from ml.domain.workflow.agent.tools.tool_registry import (
    get_tool,
    get_tool_registry,
    initialize_tools,
    register_tool,
)
from ml.domain.workflow.agent.tools.websearch.tool import WebSearchTool
from ml.domain.workflow.agent.tools.final_answer.tool import FinalAnswerTool
from ml.domain.workflow.agent.tools.file_writer.tool import FileWriterTool


class _DummyTool(BaseTool):
    def __init__(self, tool_name: str) -> None:
        self._tool_name = tool_name

    @property
    def name(self) -> str:
        return self._tool_name

    @property
    def description(self) -> str:
        return "dummy tool for testing"

    @property
    def schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, **kwargs: Any) -> ToolResult:
        return ToolResult(success=True, data=kwargs)


@pytest.fixture()
def clean_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ml.domain.workflow.agent.tools.tool_registry._tool_registry", {})


@pytest.mark.usefixtures("clean_registry")
def test_register_and_lookup_tool() -> None:
    tool = _DummyTool("dummy")

    register_tool(tool)

    registry = get_tool_registry()

    assert registry.get("dummy") is tool
    assert get_tool("dummy") is tool


@pytest.mark.usefixtures("clean_registry")
def test_duplicate_registration_overrides_previous_tool() -> None:
    first_tool = _DummyTool("duplicate")
    replacement_tool = _DummyTool("duplicate")

    register_tool(first_tool)
    register_tool(replacement_tool)

    registry = get_tool_registry()

    assert registry["duplicate"] is replacement_tool
    assert registry["duplicate"] is get_tool("duplicate")


@pytest.mark.usefixtures("clean_registry")
def test_initialize_tools_registers_default_tools() -> None:
    initialize_tools()

    registry = get_tool_registry()

    assert set(registry) == {"web_search", "final_answer", "file_writer"}
    assert isinstance(registry["web_search"], WebSearchTool)
    assert isinstance(registry["final_answer"], FinalAnswerTool)
    assert isinstance(registry["file_writer"], FileWriterTool)

    for name in registry:
        assert get_tool(name) is registry[name]
