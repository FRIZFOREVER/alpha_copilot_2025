"""Minimal prompt builder for the thinking planner."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory


class ThinkingPlannerAction(BaseModel):
    """Structured response describing the next tool call."""

    tool_name: str = Field(description="Name of the tool that must be executed next")
    arguments: dict[str, str] = Field(
        default_factory=dict,
        description="Keyword arguments that should be passed to the tool",
    )


def _format_tool_catalog(tools: Sequence[BaseTool]) -> str:
    if not tools:
        return "Нет доступных инструментов"
    lines: list[str] = []
    for tool in tools:
        schema_description = str(tool.schema)
        lines.append(
            "- "
            + tool.name
            + "\n  Описание: "
            + tool.description
            + "\n  Аргументы: "
            + schema_description
        )
    return "\n".join(lines)


def get_thinking_planner_prompt(
    *, user_request: str, available_tools: Sequence[BaseTool]
) -> ChatHistory:
    """Compose a prompt that only focuses on the latest user request."""

    prompt = ChatHistory()
    instructions: list[str] = []
    instructions.append("Ты планировщик, работающий только с последним сообщением пользователя.")
    instructions.append("Сначала сделай скрытое рассуждение, его не нужно выводить.")
    instructions.append(
        "Затем выбери один инструмент из списка ниже и подготовь JSON с полями tool_name и arguments."
    )
    instructions.append(
        "Если инструмент не нужен, верни пустую строку в tool_name и пустой объект arguments."
    )
    instructions.append("Не добавляй никаких пояснений, выводи только JSON-объект.")

    tool_block = _format_tool_catalog(available_tools)
    system_message = "\n".join(instructions) + "\n\nСписок инструментов:\n" + tool_block
    prompt.add_or_change_system(system_message)

    user_message = "Запрос пользователя:\n" + user_request + "\n\nВерни JSON сейчас."
    prompt.add_user(user_message)
    return prompt
