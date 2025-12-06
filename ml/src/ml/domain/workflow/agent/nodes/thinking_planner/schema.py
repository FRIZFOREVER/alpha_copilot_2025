from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ThinkingPlan(BaseModel):
    thought: str = Field(description="Краткое обоснование следующего шага")
    chosen_tool: str = Field(description="Имя инструмента для вызова")
    tool_args: dict[str, Any] = Field(default_factory=dict, description="Аргументы инструмента")
