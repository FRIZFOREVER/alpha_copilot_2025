"""Подсказка для этапа рассуждений исследовательского агента."""

from collections.abc import Sequence

from ml.agent.graph.state import ResearchTurn
from ml.agent.prompts.context_blocks import (
    build_conversation_context_block,
    build_evidence_snippet_block,
    build_persona_block,
)
from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory, UserProfile


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
    evidence_snippets: Sequence[str] | None = None,
    latest_reasoning: str | None = None,
    available_tools: Sequence[BaseTool] = (),
) -> ChatHistory:
    """Создать подсказку для рассуждений без прямых транскриптов наблюдений."""

    persona_block = build_persona_block(profile)
    conversation_block = build_conversation_context_block(conversation)
    evidence_block = build_evidence_snippet_block(evidence_snippets)

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
    user_instruction = (
        "Используй доступные инструменты: "
        + tool_names
        + "\n"
        + "Определи, какая информация нужна дальше, и какой инструмент лучше всего её добыть. "
        + "Кратко опиши текущий прогресс, пробелы в знании и желаемые параметры следующего шага. "
        + "Не вставляй прямые стенограммы наблюдений. "
        + "Ответь цельным текстом (2-4 предложения) без списков и заголовков."
    )
    prompt.add_user(user_instruction)
    return prompt
