from typing import Any, Optional

from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from tool execution."""

    success: bool
    data: Any
    error: str | None = None


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]
    result: Optional[ToolResult] = None

    @property
    def tool_name(self) -> str:
        return self.name


class Evidence(BaseModel):
    tool_name: str
    summary: str
    source: ToolResult

    def get_evidence(self) -> str:
        return self.summary
