from collections.abc import Sequence

from ml.agent.graph.state import ResearchTurn
from ml.agent.prompts.context_blocks import (
    build_conversation_context_block,
    build_evidence_snippet_block,
    build_persona_block,
)
from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory, UserProfile


def _summarize_turn_history(turn_history: Sequence[ResearchTurn]) -> str:
    if not turn_history:
        return "Нет предыдущих инструментальных шагов"
    max_turns = 4
    selected = list(turn_history)[-max_turns:]
    start_index = len(turn_history) - len(selected) + 1
    lines: list[str] = []
    for offset, turn in enumerate(selected):
        index = start_index + offset
        summary = turn.reasoning_summary or "нет заметок"
        request = turn.request
        observation = turn.observation
        parts: list[str] = [f"Ход {index}: {summary}"]
        if request:
            parts.append("Инструмент: " + request.tool_name)
        if observation and observation.content:
            parts.append("Наблюдение: " + observation.content)
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def _format_tool_catalog(tools: Sequence[BaseTool]) -> str:
    if not tools:
        return "Нет доступных инструментов"
    lines: list[str] = []
    for tool in tools:
        description = tool.description
        entry = tool.name
        if description:
            entry = entry + " — " + description
        lines.append(entry)
    return "\n".join(lines)


def get_research_tool_prompt(
    *,
    profile: UserProfile,
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    latest_reasoning: str,
    suggested_tool: str | None,
    desired_information: str | None,
    evidence_snippets: Sequence[str] | None,
    available_tools: Sequence[BaseTool],
) -> ChatHistory:
    """Build a prompt that lets the tool node choose and execute the next action."""

    persona_block = build_persona_block(profile)
    conversation_block = build_conversation_context_block(conversation)
    evidence_block = build_evidence_snippet_block(evidence_snippets)
    turn_summary = _summarize_turn_history(turn_history)
    tools_block = _format_tool_catalog(available_tools)

    reasoning_lines: list[str] = ["Последнее рассуждение исполнителя:", latest_reasoning]
    if suggested_tool:
        reasoning_lines.append("Предложенный инструмент: " + suggested_tool)
    if desired_information:
        reasoning_lines.append("Цель/ожидаемая информация: " + desired_information)

    instruction_sections: list[str] = [
        (
            "Ты управляешь инструментами исследовательского агента. "
            "Выбери подходящий инструмент или заверши расследование, "
            "ориентируясь на рассуждение и контекст."
        ),
        persona_block,
        conversation_block,
        evidence_block,
        "Сводка последних шагов:\n" + turn_summary,
        "Доступные инструменты:\n" + tools_block,
        "\n".join(reasoning_lines),
    ]

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(instruction_sections))

    prompt.add_user(
        "Верни решение в структурированном виде. Допустимые действия: "
        "'call_tool' (с указанием названия и аргументов) или 'finalize_answer'. "
        "Если выбираешь web_search, сформулируй осмысленный поисковый запрос, "
        "который соответствует цели и не повторяет рассуждение дословно."
    )
    return prompt
