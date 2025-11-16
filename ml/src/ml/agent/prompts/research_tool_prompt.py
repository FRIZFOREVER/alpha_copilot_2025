from collections.abc import Sequence

from ml.agent.prompts.context_blocks import (
    build_conversation_context_block,
    build_evidence_snippet_block,
    build_persona_block,
)
from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory, UserProfile


def _format_tool_catalog(tools: Sequence[BaseTool]) -> str:
    lines: list[str] = []
    for tool in tools:
        description: str = tool.description
        entry: str = tool.name
        if description:
            entry = entry + " — " + description
        lines.append(entry)
    return "\n".join(lines)


def get_research_tool_prompt(
    *,
    profile: UserProfile,
    conversation: ChatHistory,
    latest_reasoning: str,
    evidence_snippets: Sequence[str] | None,
    available_tools: Sequence[BaseTool],
) -> ChatHistory:
    """Build a prompt that lets the tool node choose and execute the next action."""

    persona_block: str = build_persona_block(profile)
    conversation_block: str = build_conversation_context_block(conversation)
    evidence_block: str = build_evidence_snippet_block(evidence_snippets)
    tools_block: str = _format_tool_catalog(available_tools)

    reasoning_lines: list[str] = [
        "Последнее рассуждение исполнителя:",
        latest_reasoning,
        "Опиши следующий шаг, пользуясь рассуждением и контекстом.",
    ]

    instruction_sections: list[str] = [
        (
            "Ты управляешь инструментами исследовательского агента. "
            "Выбери подходящий инструмент или заверши расследование, "
            "ориентируясь на рассуждение и контекст."
        ),
        persona_block,
        conversation_block,
        evidence_block,
        "Доступные инструменты:\n" + tools_block,
        "\n".join(reasoning_lines),
    ]

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(instruction_sections))

    prompt.add_user(
        "Верни решение в структурированном виде. Допустимые действия: "
        "'call_tool' (с указанием названия и аргументов) или 'finalize_answer'. \n"
        "При выборе исходи из последнего рассуждения исполнителя"
        "Если выбираешь web_search, сформулируй осмысленный поисковый запрос, "
        "который соответствует цели и не повторяет рассуждение дословно."
    )
    return prompt
