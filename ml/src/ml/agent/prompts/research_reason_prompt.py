"""Prompt builder for the reasoning phase of the research agent."""

from typing import Optional, Sequence

from ml.agent.graph.state import ResearchTurn
from ml.configs.message import ChatHistory, Role


def _format_conversation(conversation: ChatHistory) -> str:
    lines: list[str] = []
    role_labels = {
        Role.system: "System",
        Role.user: "User",
        Role.assistant: "Assistant",
    }
    for message in conversation.messages:
        role_label = role_labels.get(message.role, message.role.value)
        lines.append(f"{role_label}: {message.content}")
    return "\n".join(lines)


def _format_turn_history(turn_history: Sequence[ResearchTurn]) -> str:
    lines: list[str] = []
    for index, turn in enumerate(turn_history, start=1):
        if turn.reasoning_summary:
            lines.append(
                f"Turn {index} reasoning: {turn.reasoning_summary}"
            )
        if turn.request:
            request = turn.request
            lines.append(
                f"Turn {index} tool request: {request.tool_name} -> {request.input_text}"
            )
        if turn.observation:
            observation = turn.observation
            lines.append(
                f"Turn {index} observation: {observation.content}"
            )
    return "\n".join(lines)


def get_research_reason_prompt(
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    latest_reasoning: Optional[str] = None,
) -> ChatHistory:
    """Build a reasoning prompt with prior turns and optional scratchpad."""

    prompt = ChatHistory()
    prompt.add_or_change_system(
        (
            "You are an expert research strategist coordinating a multi-step investigation.\n"
            "Review the conversation, reference the completed research turns, and decide on the next reasoning step.\n"
            "Explain your thought process and cite which prior turn informed each decision."
        )
    )

    conversation_block = _format_conversation(conversation)
    history_block = _format_turn_history(turn_history)

    user_sections: list[str] = []
    if conversation_block:
        user_sections.append("Conversation context:\n" + conversation_block)
    else:
        user_sections.append("Conversation context:\nNo prior dialogue available.")

    if history_block:
        user_sections.append("Completed research turns:\n" + history_block)
    else:
        user_sections.append("Completed research turns:\nNone. This will be the first reasoning step.")

    if latest_reasoning:
        user_sections.append("Most recent scratchpad thoughts:\n" + latest_reasoning)

    user_sections.append(
        (
            "Provide the next reasoning summary.\n"
            "Focus on the key question, reference useful prior evidence, and recommend whether to call a tool or synthesize findings."
        )
    )

    prompt.add_user("\n\n".join(user_sections))
    return prompt
