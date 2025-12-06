from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class PlannedToolCall(BaseModel):
    thought: str
    chosen_tool: str
    tool_args: dict[str, Any]
