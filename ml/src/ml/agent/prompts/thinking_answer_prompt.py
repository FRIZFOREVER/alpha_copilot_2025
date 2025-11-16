"""Prompt builder for the thinking answer stage."""

from collections.abc import Sequence

from ml.agent.prompts.system_prompt import get_system_prompt
from ml.configs.message import ChatHistory, UserProfile


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
    messages: ChatHistory,
    profile: UserProfile,
    final_answer_evidence: Sequence[str],
) -> ChatHistory:
    """Build the finalization prompt for the thinking pipeline."""

    prompt: ChatHistory = messages.model_copy(deep=True)
    persona_text = get_system_prompt(profile)

    evidence_pool = final_answer_evidence
    evidence_block = _format_evidence_section(evidence_pool)

    system_sections: list[str] = []
    system_sections.append(persona_text)
    system_sections.append(evidence_block)

    prompt.add_or_change_system("\n\n".join(system_sections))
    return prompt
