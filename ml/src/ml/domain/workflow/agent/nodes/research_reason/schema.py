from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    thought: str = Field(description="Brief reasoning before choosing tool")
    chosen_tool: str = Field(description="Name of the tool to call next")
    tool_args: dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool")
