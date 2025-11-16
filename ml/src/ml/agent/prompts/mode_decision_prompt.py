"""Prompt builder and structured schema for selecting the reasoning mode."""

from pydantic import BaseModel, Field, field_validator

from ml.configs.message import ChatHistory, ModelMode, UserProfile


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


def _format_personal_info(profile: UserProfile) -> str | None:
    details: list[str] = []
    if profile.username:
        details.append(f"ФИО: {profile.username}")
    if profile.user_info:
        details.append(f"О себе: {profile.user_info}")
    if profile.business_info:
        details.append(f"Про бизнес: {profile.business_info}")
    if profile.additional_instructions:
        details.append(f"Дополнительные инструкции: {profile.additional_instructions}")
    if not details:
        return None
    return " | ".join(details)


def get_mode_decision_prompt(*, profile: UserProfile, history: ChatHistory) -> ChatHistory:
    """Inject system instructions for selecting the reasoning mode."""

    prompt = history.model_copy(deep=True)

    system_sections: list[str] = [
        "Вы — диспетчер, выбирающий стратегию ответа (fast/thinking/research) для ассистента.",
        (
            "Отвечайте ТОЛЬКО одним JSON-объектом с единственным полем mode, "
            'например {"mode":"thinking"}.'
        ),
        (
            "Fast — когда ответ уже есть в истории, и от пользователя требуется лишь уточнение, "
            "либо зарпос пользователяочень простой и не требует уточнения информации в интернете. "
            "Thinking — для рассуждений, планов и рекомендаций. "
            "Research — для генерации новых идей или глубокого анализа, требующих инструментов."
        ),
        "Не добавляйте пояснений, только поставьте нужный режим.",
    ]

    personal_info = _format_personal_info(profile)
    if personal_info:
        system_sections.append("Персональные сведения пользователя: " + personal_info)

    prompt.add_or_change_system("\n\n".join(system_sections))
    return prompt
