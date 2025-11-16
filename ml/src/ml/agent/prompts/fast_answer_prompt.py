"""Helpers for composing the fast-answer final prompt."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from ml.agent.graph.state import GraphState
from ml.agent.prompts.system_prompt import extract_system_prompt
from ml.configs.message import ChatHistory, Role

logger: logging.Logger = logging.getLogger(__name__)


def _format_numbered_section(title: str, lines: Sequence[str]) -> str:
    numbered_lines: list[str] = []
    position = 1
    for line in lines:
        numbered_lines.append(str(position) + ". " + line)
        position += 1
    return title + "\n" + "\n".join(numbered_lines)


def compose_fast_final_prompt(state: GraphState) -> ChatHistory:
    """Clone chat history and enrich the system prompt for the fast path."""

    chat_copy: ChatHistory = state.payload.messages.model_copy(deep=True)

    persona_prompt: str = extract_system_prompt(chat_copy)
    system_sections: list[str] = [persona_prompt]

    memories: Sequence[str] = state.memories.extracted_memories
    if memories:
        system_sections.append(
            _format_numbered_section("Извлечённые воспоминания:", memories)
        )

    evidence: Sequence[str] = state.final_answer_evidence
    if evidence:
        system_sections.append(
            _format_numbered_section("Собранные факты:", evidence)
        )

    try:
        system_message = next(message for message in chat_copy.messages if message.role == Role.system)
    except StopIteration as error:
        logger.exception("System message missing while composing fast final prompt")
        raise RuntimeError("Expected a system message inside chat history") from error

    system_message.content = "\n\n".join(system_sections)

    return chat_copy
