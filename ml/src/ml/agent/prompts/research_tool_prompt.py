"""Prompt builder for selecting and preparing a tool call."""

from collections.abc import Mapping, Sequence

from ml.agent.graph.state import ResearchToolRequest, ResearchTurn
from ml.agent.prompts.context_blocks import build_persona_block
from ml.configs.message import ChatHistory, Role, UserProfile


def _build_dialogue_snapshot(conversation: ChatHistory) -> str:
    """Summarize the dialogue for quick reference."""

    messages = conversation.messages
    role_labels = {
        Role.system: "System",
        Role.user: "User",
        Role.assistant: "Assistant",
    }
    lines: list[str] = []
    for message in messages:
        role_label = role_labels.get(message.role, message.role.value)
        lines.append(f"{role_label}: {message.content}")
    return "Dialogue snapshot:\n" + "\n".join(lines)


def _format_turn_highlights(turn_history: Sequence[ResearchTurn], *, limit: int = 3) -> str:
    """Return a compact summary of the most recent research turns."""

    recent_turns = list(turn_history)[-limit:]
    start_index = len(turn_history) - len(recent_turns) + 1
    lines: list[str] = []
    for offset, turn in enumerate(recent_turns):
        turn_number = start_index + offset
        if turn.reasoning_summary:
            lines.append(f"Turn {turn_number} reasoning: {turn.reasoning_summary}")
        if turn.request:
            request = turn.request
            lines.append(
                f"Turn {turn_number} tool request: {request.tool_name} -> {request.input_text}"
            )
        if turn.observation:
            observation = turn.observation
            lines.append(f"Turn {turn_number} observation: {observation.content}")
    return "\n".join(lines)


def _format_metadata(metadata: Mapping[str, object]) -> str:
    lines: list[str] = []
    for key, value in metadata.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _build_pending_request_block(pending_request: ResearchToolRequest) -> str:
    lines: list[str] = [
        "Pending tool request:",
        f"Tool name: {pending_request.tool_name}",
        f"Proposed input: {pending_request.input_text}",
    ]
    if pending_request.arguments:
        lines.append("Arguments:")
        for key, value in pending_request.arguments.items():
            lines.append(f"  - {key}: {value}")
    metadata_block = _format_metadata(pending_request.metadata)
    if metadata_block:
        lines.append("Metadata:")
        lines.append(metadata_block)
    return "\n".join(lines)


def get_research_tool_prompt(
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    pending_request: ResearchToolRequest,
    comparison_note: str | None = None,
    profile: UserProfile | None = None,
) -> ChatHistory:
    """Build a prompt for validating and finalizing the next tool request."""

    persona_block = build_persona_block(profile) if profile else None
    conversation_block = _build_dialogue_snapshot(conversation)
    history_block = _format_turn_highlights(turn_history) if turn_history else ""
    request_block = _build_pending_request_block(pending_request)

    evidence_sections: list[str] = []
    if persona_block:
        evidence_sections.append(persona_block)
    evidence_sections.append(conversation_block)
    if history_block:
        evidence_sections.append("Recent research turns:\n" + history_block)
    else:
        evidence_sections.append(
            "Recent research turns:\nNone. This is the first tool call under consideration."
        )
    evidence_sections.append(request_block)
    if comparison_note:
        evidence_sections.append("Comparison notes:\n" + comparison_note)

    system_sections: list[str] = [
        (
            "You are responsible for crafting the exact tool call for the research agent.\n"
            "Use the persona, dialogue snapshot, and evidence list to justify or adjust the request.\n"
            "Confirm the best tool, refine the input, and ensure the call advances the investigation."
        ),
        "\n\n".join(evidence_sections),
    ]

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(system_sections))

    prompt.add_user(
        "Validate the pending tool call using the evidence above. "
        "Respond ONLY with a JSON object that follows this schema: "
        '{"action": "call_tool" | "finalize_answer", '
        '"tool_name": string | null, "arguments": object, "justification": string}. '
        "When action is 'call_tool', provide a registered tool name, populate arguments with the "
        "exact strings that should be issued to the tool (include a 'query' field for web_search), "
        "and explain the justification using the cited evidence. When action is 'finalize_answer', "
        "omit the tool name, leave arguments empty, and justify why the current evidence is enough." 
        "Do not add commentary outside the JSON response."
    )
    return prompt
