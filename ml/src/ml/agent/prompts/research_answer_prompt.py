"""Prompt helper for assembling the final research answer."""

from collections.abc import Sequence

from ml.agent.graph.state import ResearchTurn
from ml.configs.message import ChatHistory, Message, Role


def _compress_dialogue(messages: Sequence[Message], limit: int = 6) -> str:
    selected = list(messages[-limit:])
    lines: list[str] = []
    for message in selected:
        if message.role == Role.system:
            prefix = "Система"
        elif message.role == Role.user:
            prefix = "Пользователь"
        else:
            prefix = "Ассистент"
        lines.append(f"{prefix}: {message.content}")
    return "\n".join(lines)


def _summarize_turns(turn_history: Sequence[ResearchTurn], limit: int = 5) -> str:
    summaries: list[str] = []
    for index, turn in enumerate(turn_history[-limit:], start=1):
        note = turn.reasoning_summary or "Нет заметок"
        summaries.append(f"Шаг {index}: {note}")
        observation = turn.observation
        if observation and observation.content:
            summaries.append(f"Наблюдение: {observation.content}")
    return "\n".join(summaries)


def _format_evidence(evidence_snippets: Sequence[str]) -> str:
    lines: list[str] = []
    for index, snippet in enumerate(evidence_snippets, start=1):
        lines.append(f"[{index}] {snippet}")
    return "\n".join(lines)


def get_research_answer_prompt(
    *,
    system_prompt: str,
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    answer_draft: str,
    evidence_snippets: Sequence[str],
) -> ChatHistory:
    prompt = ChatHistory()
    prompt.add_or_change_system(system_prompt)

    context_block = _compress_dialogue(conversation.messages)
    history_block = _summarize_turns(turn_history)
    evidence_block = _format_evidence(evidence_snippets)

    user_sections: list[str] = []
    if context_block:
        user_sections.append("Краткий контекст:\n" + context_block)
    if history_block:
        user_sections.append("Хронология исследования:\n" + history_block)
    user_sections.append("Черновик ответа:\n" + answer_draft)
    if evidence_block:
        user_sections.append("Источники:\n" + evidence_block)
    user_sections.append(
        "Сформируй развёрнутый финальный ответ для пользователя на основе черновика и сведений из"
        " источников. Укажи конкретные сайты или публикации, из которых взята информация,"
        " и оформи блок с источниками отдельным списком. Ответ должен быть самодостаточным,"
        " содержательным и структурированным (используй подзаголовки или списки для рецептов,"
        ' этапов и рекомендаций). Не начинай ответ с формулировок вроде "Ответ пользователя" и'
        " не предлагай продолжить исследование — считаем, что найден максимум информации.\n"
        "Не указывай источники, содержащие нерелевантную информацию\n"
        "Если все источники неревантны, то скажи, что не смог найти подходящую информацию"
    )

    prompt.add_user("\n\n".join(user_sections))
    return prompt
