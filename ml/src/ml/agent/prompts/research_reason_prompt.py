"""Подсказка для этапа рассуждений исследовательского агента."""

from collections.abc import Sequence

from ml.agent.graph.state import ResearchTurn
from ml.agent.prompts.context_blocks import (
    build_conversation_context_block,
    build_evidence_snippet_block,
)
from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory, UserProfile


def _summarize_turn_history(turn_history: Sequence[ResearchTurn]) -> str:
    if not turn_history:
        return "Сводка предыдущих шагов:\nотсутствуют"
    max_turns = 3
    selected = list(turn_history)[-max_turns:]
    start_index = len(turn_history) - len(selected) + 1
    lines: list[str] = ["Сводка предыдущих шагов:"]
    for offset, turn in enumerate(selected):
        index = start_index + offset
        summary = turn.reasoning_summary or "нет заметок"
        request = turn.request
        observation = turn.observation
        parts: list[str] = [f"Шаг {index}: {summary}"]
        if request:
            parts.append("Инструмент: " + request.tool_name)
        if observation and observation.content:
            parts.append("Наблюдение: " + observation.content)
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def _format_tool_catalog(tools: Sequence[BaseTool]) -> str:
    if not tools:
        return "Доступные инструменты:\nнет зарегистрированных инструментов"
    lines: list[str] = ["Доступные инструменты:"]
    for tool in tools:
        description = tool.description
        entry = "- " + tool.name
        if description:
            entry = entry + ": " + description
        lines.append(entry)
    return "\n".join(lines)


def _build_persona_block(profile: UserProfile) -> str:
    """Assemble a compact persona paragraph for the research reason prompt."""
    sentences: list[str] = []

    if profile.username:
        sentences.append(f"Фио пользователя или как к нему обращаться: {profile.username}.")

    if profile.user_info:
        sentences.append(f"Пользователь сам описывает себя так: {profile.user_info}.")

    if profile.additional_instructions:
        sentences.append(
            f"Дополнительные установки от пользователя: {profile.additional_instructions}."
        )

    if not sentences:
        return "Персональный контекст пользователя: сведений не указано."

    return "Персональный контекст пользователя: " + " ".join(sentences)


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

    persona_block = _build_persona_block(profile)
    conversation_block = build_conversation_context_block(conversation)
    evidence_block = build_evidence_snippet_block(evidence_snippets)
    turn_summary = _summarize_turn_history(turn_history)
    tools_block = _format_tool_catalog(available_tools)

    sections: list[str] = [
        (
            "Ты эксперт по многошаговым исследованиям. "
            "Изучи диалог, подтверждения и доступные инструменты, затем сформулируй цель "
            "для следующего шага."
        ),
        persona_block,
        conversation_block,
        evidence_block,
        turn_summary,
        tools_block,
    ]

    if latest_reasoning:
        sections.append("Последняя заметка исполнителя:\n" + latest_reasoning)

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(sections))

    user_instruction = (
        "Сначала молча проанализируй весь предоставленный контекст: профиль пользователя, "
        "историю диалога, подтверждённые фрагменты и сводку шагов. Используй только те части, "
        "которые явно связаны с текущим запросом и исследовательской задачей, игнорируя остальное. "
        "Если запрос пользователя не имеет отношения к его бизнесу, то сфокусируйся на его выполнении "
        "не беря в рассчёт его персональную информацию. "
        "Внутренне рассмотрим несколько возможных направлений исследования (So-CoT), сравни их и выбери "
        "наиболее перспективное, но в ответе покажи только итоговый вывод. Если текущих данных действительно "
        "недостаточно, кратко укажи, каких сведений не хватает и что именно нужно выяснить дальше. Если данных "
        "уже достаточно для обоснованного шага, не говори, что их мало — просто утвердительно опиши следующий "
        "шаг исследования и цель этого шага. "
        "Пиши кратко, в 3–5 связанных предложениях, без заголовков, списков "
        "и шаблонов, только ясное описание следующего шага и того, на какую информацию он нацелен. "
        "Если информации достаточно, то не занимайся её сравнением и подтверждением, а просто "
        "чётко сформулируй запрос на необходимость вызова финального ответа. "
    )

    prompt.add_user(user_instruction)
    return prompt
