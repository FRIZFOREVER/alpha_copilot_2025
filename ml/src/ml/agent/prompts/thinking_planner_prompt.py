"""Minimal prompt builder for the thinking planner."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory, Message, Role, UserProfile


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


def _find_last_user_message(messages: ChatHistory) -> tuple[int | None, str | None]:
    for index in range(len(messages.messages) - 1, -1, -1):
        message = messages.messages[index]
        if message.role == Role.user:
            return index, message.content
    return None, None


def _build_history_text(messages: Sequence[Message]) -> str | None:
    role_labels: dict[Role, str] = {
        Role.user: "Пользователь",
        Role.assistant: "Ассистент",
    }

    entries: list[str] = []
    for message in messages:
        if message.role == Role.system:
            continue
        label = role_labels.get(message.role, message.role.value.capitalize())
        entries.append(f"{label}: {message.content}")

    if not entries:
        return None
    return "\n".join(entries)


def get_thinking_planner_prompt(
    *, profile: UserProfile, messages: ChatHistory, available_tools: Sequence[BaseTool]
) -> ChatHistory:
    """Compose a prompt that only focuses on the latest user request."""

    prompt = ChatHistory()
    instructions: list[str] = []
    instructions.append(f"Обращение к пользователю: {profile.username}")
    instructions.append(f"Информация пользователя о себе: {profile.user_info}")
    instructions.append(f"Информация пользователя о его бизнесе: {profile.business_info}")
    instructions.append(
        f"Дополнительные инструкциии пользователя: {profile.additional_instructions}"
    )
    instructions.append("Не используй эту персональную информацию при планировании задач")
    instructions.append("Ты планировщик, работающий только с последним сообщением пользователя.")
    instructions.append("Сначала сделай скрытое рассуждение, его не нужно выводить.")
    instructions.append(
        "Затем выбери один инструмент из списка ниже и подготовь JSON с полями tool_name и arguments."
    )
    instructions.append(
        "Если инструмент не нужен, верни пустую строку в tool_name и пустой объект arguments."
    )
    instructions.append("Не добавляй никаких пояснений, выводи только JSON-объект.")

    last_user_index, last_user_content = _find_last_user_message(messages)
    if last_user_index is not None:
        history_messages = messages.messages[:last_user_index]
    else:
        history_messages = messages.messages[:-1]
    history_text = _build_history_text(history_messages)
    if history_text:
        instructions.append("История сообщений до последнего запроса:\n" + history_text)

    tool_block = _format_tool_catalog(available_tools)
    system_message = "\n".join(instructions) + "\n\nСписок инструментов:\n" + tool_block
    prompt.add_or_change_system(system_message)

    if last_user_content is None:
        if messages.messages:
            last_user_content = messages.messages[-1].content
        else:
            last_user_content = "Нет сообщений для анализа."

    user_message = "Запрос пользователя:\n" + last_user_content
    prompt.add_user(user_message)
    return prompt
