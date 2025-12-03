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


class Evidence(BaseModel):
    evidence: str
    source: ToolResult

    def get_evidence(self) -> str:
        return self.evidence
