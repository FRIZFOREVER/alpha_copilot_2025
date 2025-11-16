"""Подсказка для этапа рассуждений исследовательского агента."""

from collections.abc import Sequence

from ml.agent.graph.state import ResearchTurn
from ml.agent.prompts.context_blocks import (
    build_conversation_context_block,
    build_persona_block,
)
from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory, UserProfile


def _build_evidence_block(turn_history: Sequence[ResearchTurn]) -> str:
    evidence_lines: list[str] = []
    for turn in turn_history:
        observation = turn.observation
        if observation is None:
            continue
        summary = None
        metadata = observation.metadata
        if metadata and hasattr(metadata, "get"):
            summary_value = metadata.get("summary")
            if isinstance(summary_value, str) and summary_value != "":
                summary = summary_value
        if summary is None:
            tool_name = observation.tool_name or "Неизвестный инструмент"
            keys: list[str] = []
            if metadata:
                for key in metadata.keys():
                    keys.append(str(key))
            if keys:
                summary = "данные получены, атрибуты: " + ", ".join(keys)
            else:
                summary = "данные получены без дополнительных атрибутов"
            evidence_lines.append("- " + tool_name + ": " + summary)
            continue
        tool_label = observation.tool_name or "Неизвестный инструмент"
        evidence_lines.append("- " + tool_label + ": " + summary)
    if not evidence_lines:
        return "Список подтверждений:\nнет зарегистрированных наблюдений"
    return "Список подтверждений:\n" + "\n".join(evidence_lines)


def _format_tool_names(tools: Sequence[BaseTool]) -> str:
    if not tools:
        return "нет доступных инструментов"
    names: list[str] = []
    for tool in tools:
        names.append(tool.name)
    return ", ".join(names)


def get_research_reason_prompt(
    *,
    profile: UserProfile,
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    latest_reasoning: str | None = None,
    available_tools: Sequence[BaseTool] = (),
) -> ChatHistory:
    """Создать подсказку для рассуждений без прямых транскриптов наблюдений."""

    persona_block = build_persona_block(profile)
    conversation_block = build_conversation_context_block(conversation)
    evidence_block = _build_evidence_block(turn_history)

    sections: list[str] = [
        (
            "Ты эксперт по многошаговым исследованиям. "
            "Изучи диалог и накопленные подтверждения, чтобы подготовить следующий вызов инструмента."
        ),
        persona_block,
        conversation_block,
        evidence_block,
    ]

    if latest_reasoning:
        sections.append("Последняя заметка исполнителя:\n" + latest_reasoning)

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(sections))

    tool_names = _format_tool_names(available_tools)
    response_format = (
        "Reason:\n<краткое объяснение логики>\n"
        "Suggested tool:\n<название инструмента из списка>\n"
        "Call plan:\nObjective: <цель вызова>\n"
        "<ключ1>: <значение1>\n<ключ2>: <значение2>\n..."
    )
    user_instruction = (
        "Используй доступные инструменты: "
        + tool_names
        + "\n"
        + "Никогда не вставляй прямые стенограммы наблюдений. "
        + "Ответь строго по шаблону ниже, не добавляя других секций.\n"
        + response_format
        + "\nОбязательно перечисли аргументы для выбранного инструмента в Call plan,"
        + " а также укажи Comparison_text, если нужно сверить будущие результаты."
    )
    prompt.add_user(user_instruction)
    return prompt
