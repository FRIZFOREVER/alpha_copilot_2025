"""Prompt builder for selecting and preparing a tool call."""

from typing import Mapping, Optional, Sequence

from ml.agent.graph.state import ResearchToolRequest, ResearchTurn
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


def _format_metadata(metadata: Mapping[str, object]) -> str:
    lines: list[str] = []
    for key, value in metadata.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def get_research_tool_prompt(
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    pending_request: ResearchToolRequest,
    comparison_note: Optional[str] = None,
) -> ChatHistory:
    """Build a prompt for validating and finalizing the next tool request."""

    prompt = ChatHistory()
    prompt.add_or_change_system(
        (
            "You are responsible for crafting the exact tool call for the research agent.\n"
            "Use the conversation and research history to justify the request.\n"
            "Confirm the best tool, refine the input, and explain why this call moves the investigation forward."
        )
    )

    conversation_block = _format_conversation(conversation)
    history_block = _format_turn_history(turn_history)
    metadata_block = _format_metadata(pending_request.metadata)

    user_sections: list[str] = []
    if conversation_block:
        user_sections.append("Conversation context:\n" + conversation_block)
    else:
        user_sections.append("Conversation context:\nNo prior dialogue available.")

    if history_block:
        user_sections.append("Completed research turns:\n" + history_block)
    else:
        user_sections.append("Completed research turns:\nNone. This is the first tool call under consideration.")

    request_lines: list[str] = [
        "Pending tool request:",
        f"Tool name: {pending_request.tool_name}",
        f"Proposed input: {pending_request.input_text}",
    ]
    if metadata_block:
        request_lines.append("Metadata:")
        request_lines.append(metadata_block)
    user_sections.append("\n".join(request_lines))

    if comparison_note:
        user_sections.append("Comparison notes:\n" + comparison_note)

    user_sections.append(
        (
            "Decide how to execute the tool call.\n"
            "Respond with a structured summary that includes the final tool name, the refined input, and a short justification referencing the context."
        )
    )

    prompt.add_user("\n\n".join(user_sections))
    return prompt
