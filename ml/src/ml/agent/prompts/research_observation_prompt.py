"""Prompt builder for synthesizing tool observations."""

from typing import Sequence

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


def _format_documents(tool_name: str, documents: Sequence[str]) -> str:
    if not documents:
        return "No new documents were retrieved."
    lines: list[str] = []
    for index, document in enumerate(documents, start=1):
        lines.append(f"Document {index} ({tool_name}): {document}")
    return "\n".join(lines)


def get_research_observation_prompt(
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    tool_name: str,
    documents: Sequence[str],
) -> ChatHistory:
    """Build a prompt for interpreting tool outputs and updating the plan."""

    prompt = ChatHistory()
    prompt.add_or_change_system(
        (
            "You are an analytical researcher reviewing newly fetched evidence.\n"
            "Combine the tool output with the existing research plan and explain how it influences the next steps."
        )
    )

    conversation_block = _format_conversation(conversation)
    history_block = _format_turn_history(turn_history)
    documents_block = _format_documents(tool_name, documents)

    user_sections: list[str] = []
    if conversation_block:
        user_sections.append("Conversation context:\n" + conversation_block)
    else:
        user_sections.append("Conversation context:\nNo prior dialogue available.")

    if history_block:
        user_sections.append("Completed research turns:\n" + history_block)
    else:
        user_sections.append("Completed research turns:\nNone recorded before this observation.")

    user_sections.append("Latest tool evidence:\n" + documents_block)

    user_sections.append(
        (
            "Summarize the key insights from the evidence.\n"
            "Highlight contradictions or confirmations relative to earlier turns and propose the next action."
        )
    )

    prompt.add_user("\n\n".join(user_sections))
    return prompt
