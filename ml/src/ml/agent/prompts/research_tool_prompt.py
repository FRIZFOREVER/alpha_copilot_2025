"""Prompt builder for selecting and preparing a tool call."""

from collections.abc import Sequence

from ml.agent.graph.state import ResearchTurn
from ml.agent.prompts.context_blocks import build_persona_block
from ml.agent.tools.base import BaseTool
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


def _format_tool_catalog(tools: Sequence[BaseTool]) -> str:
    if not tools:
        return "Доступные инструменты: отсутствуют"
    lines: list[str] = ["Доступные инструменты:"]
    for tool in tools:
        lines.append(f"- {tool.name}: {tool.description}")
    return "\n".join(lines)


def _build_reasoning_block(reasoning: str | None) -> str:
    if not reasoning:
        return ""
    return "Последняя заметка исследователя:\n" + reasoning


def get_research_tool_prompt(
    conversation: ChatHistory,
    turn_history: Sequence[ResearchTurn],
    available_tools: Sequence[BaseTool],
    *,
    latest_reasoning: str | None = None,
    profile: UserProfile | None = None,
) -> ChatHistory:
    """Build a prompt for selecting and finalizing the next tool request."""

    persona_block = build_persona_block(profile) if profile else None
    conversation_block = _build_dialogue_snapshot(conversation)
    history_block = _format_turn_highlights(turn_history) if turn_history else ""
    reasoning_block = _build_reasoning_block(latest_reasoning)
    tools_block = _format_tool_catalog(available_tools)

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
    if reasoning_block:
        evidence_sections.append(reasoning_block)
    evidence_sections.append(tools_block)

    system_sections: list[str] = [
        (
            "You are responsible for crafting the exact tool call for the research agent.\n"
            "Use the persona, dialogue snapshot, and evidence list to choose the best next step.\n"
            "Confirm the best tool, craft the required arguments, and ensure the call advances the investigation."
        ),
        "\n\n".join(evidence_sections),
    ]

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(system_sections))

    prompt.add_user(
        "Реши, нужно ли вызвать инструмент или можно перейти к финальному ответу. "
        "Ответь ТОЛЬКО JSON объектом со структурой "
        '{"action": "call_tool" | "finalize_answer", '
        '"tool_name": string | null, "arguments": object, "justification": string}. '
        "Если выбираешь 'call_tool', используй одно из доступных названий, заполни аргументы "
        "строками, перечисли обязательные поля (например, query для web_search) и объясни "
        "обоснование. Если выбираешь 'finalize_answer', tool_name = null и arguments = {}. "
        "Не добавляй комментариев вне JSON."
    )
    return prompt
