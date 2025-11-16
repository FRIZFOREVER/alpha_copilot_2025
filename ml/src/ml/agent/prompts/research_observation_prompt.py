"""Prompt builder for synthesizing tool observations."""

from collections.abc import Sequence

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


def _format_documents(tool_name: str, documents: Sequence[str]) -> str:
    if not documents:
        return "Новых документов не получено."
    lines: list[str] = []
    for index, document in enumerate(documents, start=1):
        lines.append(f"Документ {index} ({tool_name}): {document}")
    return "\n".join(lines)


def _build_observer_persona_block(profile: UserProfile) -> str:
    """Return a persona section tailored for interpreting tool observations."""

    lines: list[str] = ["Персональный контекст пользователя для наблюдений:"]
    has_details = False

    if profile.user_info:
        lines.append(f"- Самоописание пользователя: {profile.user_info}")
        has_details = True

    if profile.business_info:
        lines.append(f"- Описание бизнеса: {profile.business_info}")
        has_details = True

    if not has_details:
        lines.append("- Пользователь не предоставил дополнительных сведений.")

    return "\n".join(lines)


def _build_latest_user_message_block(conversation: ChatHistory) -> str:
    for message in reversed(conversation.messages):
        if message.role == Role.user:
            return "Последнее сообщение пользователя:\n" + message.content
    return "Последнее сообщение пользователя:\nне найдено"


def _build_latest_reasoning_block(latest_reasoning: str | None) -> str:
    if latest_reasoning:
        return "Предыдущее рассуждение исполнителя:\n" + latest_reasoning
    return "Предыдущее рассуждение исполнителя:\nзаметок нет"


def _build_latest_request_block(latest_request: str | None, tool_name: str) -> str:
    if latest_request:
        return "Запрос, который был передан инструменту '" + tool_name + "':\n" + latest_request
    return "Запрос, который был передан инструменту '" + tool_name + "':\nописание отсутствует"


def get_research_observation_prompt(
    *,
    profile: UserProfile,
    conversation: ChatHistory,
    latest_reasoning: str | None,
    latest_request: str | None,
    tool_name: str,
    documents: Sequence[str],
) -> ChatHistory:
    """Build a prompt for interpreting tool outputs and updating the plan."""

    persona_block = _build_observer_persona_block(profile)
    latest_user_message_block = _build_latest_user_message_block(conversation)
    documents_block = "Последние данные от инструмента:\n" + _format_documents(tool_name, documents)
    reasoning_block = _build_latest_reasoning_block(latest_reasoning)
    request_block = _build_latest_request_block(latest_request, tool_name)

    system_sections: list[str] = [
        "Вы — аналитичный исследователь, который изучает новые данные и обобщает находки.",
        reasoning_block,
        documents_block,
        request_block,
        persona_block,
        latest_user_message_block,
    ]

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(system_sections))

    prompt.add_user(
        "Выдели ключевые выводы из материалов, отметь противоречия или подтверждения "
        "относительно предыдущих шагов и предложи самое логичное следующее исследовательское действие."
    )
    return prompt
