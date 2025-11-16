"""Prompt builder for synthesizing tool observations."""

import logging
from collections.abc import Sequence

from ml.configs.message import ChatHistory, Role

logger = logging.getLogger(__name__)


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


def _build_latest_reasoning_block(latest_reasoning: str) -> str:
    return "Предыдущее рассуждение исполнителя:\n" + latest_reasoning


def _build_latest_request_block(latest_request: str, tool_name: str) -> str:
    return "Запрос, который был передан инструменту '" + tool_name + "':\n" + latest_request


def get_research_observation_prompt(
    *,
    conversation: ChatHistory,
    latest_reasoning: str,
    latest_request: str,
    tool_name: str,
    documents: Sequence[str],
) -> ChatHistory:
    """Build a prompt for interpreting tool outputs and updating the shared understanding.

    This node should NOT планировать следующий шаг и НЕ выбирать инструменты.
    Его задача — зафиксировать наблюдения: что именно дали инструменты и
    как это приближает нас к ответу на исходный запрос пользователя.
    """

    try:
        latest_user_message = conversation.messages[-1]
    except IndexError as exc:  # pragma: no cover - validated upstream
        logger.exception("Conversation history is empty, cannot find the latest user message")
        raise ValueError("Conversation history is empty") from exc

    if latest_user_message.role is not Role.user:
        logger.exception("Last message is not from the user, got role %s", latest_user_message.role)
        raise ValueError("Last conversation message must belong to the user")

    latest_user_message_block = (
        "Последнее сообщение пользователя (исходный запрос, на который нужно ответить):\n"
        + latest_user_message.content
    )
    documents_block = "Последние данные от инструмента:\n" + _format_documents(tool_name, documents)
    reasoning_block = _build_latest_reasoning_block(latest_reasoning)
    request_block = _build_latest_request_block(latest_request, tool_name)

    system_sections: list[str] = [
        (
            "Вы — аналитичный исследователь-наблюдатель. Ваша задача сейчас — не планировать "
            "следующие шаги, а аккуратно зафиксировать, ЧТО ИМЕННО дали инструменты и как это "
            "помогает приблизиться к ответу на исходный запрос пользователя."
        ),
        reasoning_block,
        documents_block,
        request_block,
        latest_user_message_block,
    ]

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(system_sections))

    prompt.add_user(
        "На основе полученных данных:\n"
        "- аккуратно извлеки и запиши все ключевые факты, цифры, определения, шаги инструкций и выводы,\n"
        "  которые помогают ответить на исходный запрос пользователя;\n"
        "- отметь, какие сведения подтверждают или уточняют предыдущие рассуждения, а что остаётся неизвестным;\n"
        "- при наличии нескольких документов объединяй информацию, избегая повторов, но не теряя важных деталей.\n\n"
        "Не предлагай следующие действия, не выбирай инструменты и не формируй план. "
        "Твой ответ — это только наблюдения и выводы из материалов инструмента, в максимально полезной форме "
        "для последующего шага рассуждений."
    )
    return prompt
