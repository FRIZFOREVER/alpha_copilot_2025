"""Prompt builder and structured schema for selecting the reasoning mode."""

from pydantic import BaseModel, Field, field_validator

from ml.configs.message import ChatHistory, ModelMode, RequestPayload


class ModeDecisionResponse(BaseModel):
    """Structured response returned by the mode decision model."""

    mode: ModelMode = Field(
        description=(
            "The reasoning mode that should be used by the assistant. "
            "Must be one of: fast, thiking, research."
        ),
    )

    @field_validator("mode")
    @classmethod
    def _ensure_concrete_mode(cls, value: ModelMode) -> ModelMode:
        if value is ModelMode.Auto:
            raise ValueError("Mode decision must not return auto")
        return value


def get_mode_decision_prompt(payload: RequestPayload) -> ChatHistory:
    """Construct a prompt that asks the model to choose a reasoning mode."""

    prompt: ChatHistory = ChatHistory()

    system_sections: list[str] = []
    if payload.system:
        system_sections.append(payload.system)
    system_sections.append(
        "Ты выступаешь в роли диспетчера, который выбирает стратегию ответа для ассистента."
    )
    system_sections.append(
        "Выбери один режим из списка: fast (моментальный ответ), "
        "thiking (углублённое рассуждение) или research (исследование с инструментами)."
    )
    system_sections.append(
        "Ответ должен быть в формате JSON с единственным полем mode."
    )
    prompt.add_or_change_system("\n".join(system_sections))

    user_sections: list[str] = []
    conversation_dump: str = payload.messages.model_dump_string()
    if conversation_dump:
        user_sections.append("Диалог:\n" + conversation_dump)
    else:
        user_sections.append("Диалог:\nнет сообщений")

    if payload.tag is not None:
        user_sections.append("Текущий тег беседы: " + payload.tag.value)

    user_sections.append("Запрошенный режим: auto")
    user_sections.append(
        "Учти сложность и контекст задачи, а затем выбери наиболее подходящий режим."
    )

    prompt.add_user("\n\n".join(user_sections))

    return prompt
