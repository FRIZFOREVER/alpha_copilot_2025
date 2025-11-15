"""Prompt builder for the thinking answer stage."""

from collections.abc import Sequence

from ml.configs.message import ChatHistory


def _format_plan_section(plan_summary: str | None, plan_steps: Sequence[str]) -> str:
    sections: list[str] = []
    if plan_summary:
        sections.append("Сводка плана:\n" + plan_summary)
    if plan_steps:
        indexed_steps: list[str] = []
        index = 1
        for step in plan_steps:
            indexed_steps.append(str(index) + ". " + step)
            index += 1
        sections.append("Шаги плана:\n" + "\n".join(indexed_steps))
    return "\n\n".join(sections)


def _format_evidence_section(evidence: Sequence[str]) -> str:
    if not evidence:
        return ""
    numbered: list[str] = []
    position = 1
    for item in evidence:
        numbered.append(str(position) + ". " + item)
        position += 1
    return "Собранные факты:\n" + "\n".join(numbered)


def get_thinking_answer_prompt(
    *,
    system_prompt: str,
    conversation: ChatHistory,
    plan_summary: str | None,
    plan_steps: Sequence[str],
    evidence: Sequence[str],
    draft: str,
) -> ChatHistory:
    """Build the finalization prompt for the thinking pipeline."""

    prompt = ChatHistory()
    system_parts: list[str] = []
    system_parts.append(system_prompt)
    system_parts.append(
        "Сформируй ясный и структурированный ответ для пользователя, опираясь на собранные факты."
    )
    system_parts.append(
        "Если доказательств недостаточно, честно опиши ограничения и предложи дальнейшие шаги."
    )
    prompt.add_or_change_system("\n".join(system_parts))

    user_sections: list[str] = []
    conversation_dump = conversation.model_dump_string()
    if conversation_dump:
        user_sections.append("Диалог:\n" + conversation_dump)
    else:
        user_sections.append("Диалог:\nнет сообщений")

    plan_block = _format_plan_section(plan_summary, plan_steps)
    if plan_block:
        user_sections.append(plan_block)

    evidence_block = _format_evidence_section(evidence)
    if evidence_block:
        user_sections.append(evidence_block)

    user_sections.append("Черновик ответа:\n" + draft)
    user_sections.append(
        "Перепиши черновик в окончательный ответ. Укажи источники из списка фактов, если они добавляют ценность."
    )

    prompt.add_user("\n\n".join(user_sections))
    return prompt
