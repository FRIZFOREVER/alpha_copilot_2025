"""Reusable helpers for building conversation and evidence context blocks."""

from collections.abc import Sequence

from ml.configs.message import ChatHistory


def build_conversation_context_block(conversation: ChatHistory) -> str:
    """Summarize the latest turns of the chat for inclusion in a system prompt."""

    history = conversation.messages
    if not history:
        return "Контекст диалога:\nнет сообщений"

    lines: list[str] = []
    for message in history:
        prefix = message.role.value.upper()
        lines.append(prefix + ": " + message.content)

    header = "Контекст диалога (всего " + str(len(history)) + " сообщений):"
    return header + "\n" + "\n\n".join(lines)


def build_evidence_snippet_block(evidence_snippets: Sequence[str] | None) -> str:
    """Format collected evidence snippets for inclusion in prompts."""

    if not evidence_snippets:
        return "Список подтверждений:\nнет зарегистрированных наблюдений"

    lines: list[str] = []
    for snippet in evidence_snippets:
        if not snippet:
            continue
        lines.append("- " + snippet)

    if not lines:
        return "Список подтверждений:\nнет зарегистрированных наблюдений"

    return "Список подтверждений:\n" + "\n".join(lines)
