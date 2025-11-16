"""Построитель подсказки для этапа рассуждений исследовательского агента."""

from collections.abc import Sequence

from ml.agent.graph.state import ResearchObservation, ResearchToolRequest, ResearchTurn
from ml.agent.prompts.context_blocks import build_persona_block
from ml.configs.message import ChatHistory, Role, UserProfile


def _format_turn_history(turn_history: Sequence[ResearchTurn]) -> str:
    lines: list[str] = []
    for index, turn in enumerate(turn_history, start=1):
        lines.append(f"Ход {index} — рассуждение: {turn.reasoning_summary or 'не задано'}")
        request: ResearchToolRequest | None = turn.request
        if request:
            lines.append(
                f"Ход {index} — запрос к инструменту: {request.tool_name} -> {request.input_text}"
            )
        else:
            lines.append(f"Ход {index} — запрос к инструменту: нет")
        observation: ResearchObservation | None = turn.observation
        if observation:
            lines.append(f"Ход {index} — наблюдение: {observation.content}")
        else:
            lines.append(f"Ход {index} — наблюдение: нет")
    return "\n".join(lines)


def _format_conversation_context(conversation: ChatHistory) -> str:
    """Вернуть строку со всеми сообщениями диалога."""

    messages = conversation.messages
    lines: list[str] = []
    for message in messages:
        role_label: str | None = {
            Role.system: "SYSTEM",
            Role.user: "USER",
            Role.assistant: "ASSISTANT",
        }.get(message.role, message.role.value.upper())
        lines.append(role_label + ": " + message.content)

    header = "Контекст диалога (" + str(len(messages)) + " сообщений)"
    return header + "\n" + "\n\n".join(lines)


def get_research_reason_prompt(
    profile: UserProfile,
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    latest_reasoning: str | None = None,
) -> ChatHistory:
    """Создать подсказку для рассуждений с учётом профиля и предыдущих ходов."""

    persona_block = build_persona_block(profile)
    conversation_block = _format_conversation_context(conversation)
    history_block = _format_turn_history(turn_history)

    if history_block:
        evidence_block = "Сводка завершённых исследовательских ходов:\n" + history_block
    else:
        evidence_block = (
            "Сводка завершённых исследовательских ходов:\n"
            "Нет записанных ходов. Это первый этап рассуждений."
        )

    sections: list[str] = [
        (
            "Вы — эксперт по исследовательским стратегиям, координирующий многошаговое расследование.\n"
            "Изучи профиль пользователя, текущий диалог и накопленные доказательства, "
            "чтобы определить оптимальный следующий шаг."
        ),
        persona_block,
        conversation_block,
        evidence_block,
    ]

    if latest_reasoning:
        sections.append("Последние заметки из черновика:\n" + latest_reasoning)

    sections.append(
        "Всегда ссылайся на доступные факты из диалога и прошлых ходов, избегай повторного "
        "запроса одной и той же информации и фиксируй пробелы в данных."
    )

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(sections))

    prompt.add_user(
        "Определи следующий шаг исследования. Укажи новую сводку рассуждений, выбери одно "
        "из действий THINK (продолжить анализ), TOOL (подготовить запрос к инструменту) или FINALIZE "
        "(перейти к ответу), и объясни, какие сведения обосновывают выбор."
    )
    return prompt
