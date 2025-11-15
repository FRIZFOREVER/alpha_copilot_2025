"""Prompt builder for the thinking answer stage."""

from collections.abc import Sequence

from ml.agent.prompts.system_prompt import get_system_prompt
from ml.configs.message import ChatHistory, UserProfile


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


def _merge_evidence(
    thinking_evidence: Sequence[str], final_answer_evidence: Sequence[str]
) -> list[str]:
    merged: list[str] = []
    for evidence_bucket in (thinking_evidence, final_answer_evidence):
        for item in evidence_bucket:
            if item:
                merged.append(item)
    return merged


def _build_drafting_section(draft: str) -> str:
    sections: list[str] = []
    if draft:
        sections.append("Черновик ответа (для переработки):\n" + draft)
    sections.append(
        "Сформируй ясный и структурированный ответ для пользователя, опираясь на собранные факты."
    )
    sections.append(
        "Если доказательств недостаточно, честно опиши ограничения и предложи дальнейшие шаги."
    )
    sections.append(
        "Перепиши черновик в окончательный ответ. Укажи источники из списка фактов, если они добавляют ценность."
    )
    return "\n\n".join(sections)


def get_thinking_answer_prompt(
    *,
    conversation: ChatHistory,
    profile: UserProfile,
    plan_summary: str | None,
    plan_steps: Sequence[str],
    thinking_evidence: Sequence[str],
    final_answer_evidence: Sequence[str],
    draft: str,
) -> ChatHistory:
    """Build the finalization prompt for the thinking pipeline."""

    prompt = conversation.model_copy(deep=True)
    persona_text = get_system_prompt(profile)

    plan_block = _format_plan_section(plan_summary, plan_steps)
    evidence_pool = _merge_evidence(thinking_evidence, final_answer_evidence)
    evidence_block = _format_evidence_section(evidence_pool)
    drafting_block = _build_drafting_section(draft)

    system_sections: list[str] = []
    system_sections.append(persona_text)
    if plan_block:
        system_sections.append(plan_block)
    if evidence_block:
        system_sections.append(evidence_block)
    system_sections.append(drafting_block)

    prompt.add_or_change_system("\n\n".join(system_sections))
    return prompt
