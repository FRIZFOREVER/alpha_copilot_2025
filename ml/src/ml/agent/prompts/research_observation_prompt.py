"""Prompt builder for synthesizing tool observations."""

from collections.abc import Sequence

from ml.agent.graph.state import ResearchTurn
from ml.agent.prompts.system_prompt import get_system_prompt
from ml.configs.message import ChatHistory, Role, UserProfile


def summarize_conversation_for_observer(conversation: ChatHistory) -> str:
    """Return a condensed representation of the visible dialogue."""

    lines: list[str] = []
    role_labels: dict[Role, str] = {
        Role.system: "Система",
        Role.user: "Пользователь",
        Role.assistant: "Ассистент",
    }
    for message in conversation.messages:
        role_label: str | None = role_labels.get(message.role, message.role.value)
        lines.append(f"{role_label}: {message.content}")
    return "\n".join(lines)


def summarize_turn_history_for_observer(turn_history: Sequence[ResearchTurn]) -> str:
    """Return a condensed log of past reasoning turns."""

    lines: list[str] = []
    for index, turn in enumerate(turn_history, start=1):
        if turn.reasoning_summary:
            lines.append(f"Ход {index} — рассуждение: {turn.reasoning_summary}")
        if turn.request:
            request = turn.request
            lines.append(
                f"Ход {index} — запрос к инструменту: {request.tool_name} -> {request.input_text}"
            )
        if turn.observation:
            observation = turn.observation
            lines.append(f"Ход {index} — наблюдение: {observation.content}")
    return "\n".join(lines)


def _format_documents(tool_name: str, documents: Sequence[str]) -> str:
    if not documents:
        return "Новых документов не получено."
    lines: list[str] = []
    for index, document in enumerate(documents, start=1):
        lines.append(f"Документ {index} ({tool_name}): {document}")
    return "\n".join(lines)


def get_research_observation_prompt(
    profile: UserProfile,
    conversation_summary: str,
    turn_history_summary: str,
    tool_name: str,
    documents: Sequence[str],
) -> ChatHistory:
    """Build a prompt for interpreting tool outputs and updating the plan."""

    persona_text = get_system_prompt(profile)
    conversation_block = (
        "Контекст диалога:\n" + conversation_summary
        if conversation_summary
        else "Контекст диалога:\nПредыдущие сообщения отсутствуют."
    )
    history_block = (
        "Завершённые исследовательские ходы:\n" + turn_history_summary
        if turn_history_summary
        else "Завершённые исследовательские ходы:\nНет записей перед текущим наблюдением."
    )
    documents_block = "Последние данные от инструмента:\n" + _format_documents(tool_name, documents)

    system_sections: list[str] = [
        "Вы — аналитичный исследователь, который изучает новые данные и обобщает находки.",
        "Персона ассистента:\n" + persona_text,
        conversation_block,
        history_block,
        documents_block,
    ]

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(system_sections))

    prompt.add_user(
        "Выдели ключевые выводы из материалов, отметь противоречия или подтверждения "
        "относительно предыдущих шагов и предложи самое логичное следующее исследовательское действие."
    )
    return prompt
