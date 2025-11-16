"""Helpers for composing the fast-answer final prompt."""

from __future__ import annotations

from ml.agent.graph.state import GraphState
from ml.agent.prompts.system_prompt import get_system_prompt
from ml.configs.message import ChatHistory


def compose_fast_final_prompt(state: GraphState) -> ChatHistory:
    """Clone chat history and replace the system prompt for the fast path."""

    chat_copy: ChatHistory = state.payload.messages.model_copy(deep=True)
    persona_prompt: str = get_system_prompt(state.payload.profile)
    chat_copy.add_or_change_system(persona_prompt)
    return chat_copy
