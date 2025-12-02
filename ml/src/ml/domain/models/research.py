from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlannedToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolObservation(BaseModel):
    tool_name: str
    result: Any
