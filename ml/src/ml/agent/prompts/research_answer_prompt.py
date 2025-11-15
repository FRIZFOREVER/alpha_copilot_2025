"""Prompt helper for assembling the final research answer."""

from collections.abc import Sequence

from ml.agent.prompts.system_prompt import get_system_prompt
from ml.configs.message import ChatHistory, UserProfile


def _format_evidence(evidence_snippets: Sequence[str]) -> str:
    lines: list[str] = []
    for index, snippet in enumerate(evidence_snippets, start=1):
        lines.append(f"[{index}] {snippet}")
    return "\n".join(lines)


def _compose_system_message(
    *,
    profile: UserProfile,
    turn_highlights: Sequence[str],
    latest_reasoning: str,
    evidence_snippets: Sequence[str],
) -> str:
    persona = get_system_prompt(profile)
    sections: list[str] = [persona]

    if turn_highlights:
        highlights = "\n".join(f"- {highlight}" for highlight in turn_highlights)
        sections.append("Ключевые шаги исследования:\n" + highlights)

    if latest_reasoning:
        sections.append("Последняя сводка рассуждений:\n" + latest_reasoning)

    if evidence_snippets:
        sections.append("Доступные источники:\n" + _format_evidence(evidence_snippets))

    sections.append(
        "Правила финального ответа:\n"
        "1. Сформируй развёрнутый ответ на основе предоставленных данных.\n"
        "2. Укажи конкретные сайты или публикации и оформи блок «Источники» со ссылками на"
        " номера из списка источников.\n"
        "3. Структурируй ответ: используй подзаголовки, списки и шаги для рекомендаций.\n"
        "4. Не начинай ответ с формулировок вроде «Ответ пользователя» и не предлагай продолжить"
        " исследование.\n"
        "5. Не ссылайся на нерелевантные источники. Если все источники бесполезны, честно сообщи"
        " об этом."
    )

    return "\n\n".join(sections)


def get_research_answer_prompt(
    *,
    profile: UserProfile,
    conversation: ChatHistory,
    turn_highlights: Sequence[str],
    latest_reasoning: str,
    evidence_snippets: Sequence[str],
) -> ChatHistory:
    """Recreate the conversation with an updated system message for the final answer."""

    prompt: ChatHistory = conversation.model_copy(deep=True)
    system_message = _compose_system_message(
        profile=profile,
        turn_highlights=turn_highlights,
        latest_reasoning=latest_reasoning,
        evidence_snippets=evidence_snippets,
    )
    prompt.add_or_change_system(system_message)
    return prompt
