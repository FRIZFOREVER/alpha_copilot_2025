"""Prompt builder and structured schema for selecting the reasoning mode."""

from collections.abc import Sequence

from pydantic import BaseModel, Field, field_validator

from ml.agent.prompts.system_prompt import get_system_prompt
from ml.configs.message import ChatHistory, ModelMode, Tag, UserProfile


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


def get_mode_decision_prompt(
    *,
    profile: UserProfile,
    conversation_summary: str,
    tag: Tag | None = None,
    evidence: Sequence[str] | None = None,
) -> ChatHistory:
    """Construct a prompt that asks the model to choose a reasoning mode."""

    persona_text = get_system_prompt(profile)

    system_sections: list[str] = [
        "Ты выступаешь в роли диспетчера, который выбирает стратегию ответа для ассистента.",
        (
            "Выбери один режим из списка: fast (моментальный ответ), "
            "thinking (углублённое рассуждение) или research (исследование с инструментами)."
        ),
        "Ответ должен быть в формате JSON с единственным полем mode.",
        "Персона ассистента:\n" + persona_text,
    ]

    if conversation_summary:
        system_sections.append("Сжатая выжимка последних сообщений:\n" + conversation_summary)
    else:
        system_sections.append("Сжатая выжимка последних сообщений отсутствует.")

    if tag is not None:
        system_sections.append("Текущий тег беседы: " + tag.value)

    if evidence:
        evidence_lines = [item for item in evidence if item]
        if evidence_lines:
            formatted_evidence = "\n".join(f"- {item}" for item in evidence_lines)
            system_sections.append("Накопленные факты и наблюдения:\n" + formatted_evidence)

    prompt = ChatHistory()
    prompt.add_or_change_system("\n\n".join(system_sections))

    user_sections: list[str] = [
        "Запрошенный режим: auto",
        (
            "Стандартный режим — thinking. Используй его для большинства запросов и всегда, когда"
            " остаются сомнения.\n"
            "Режим research выбирай только если пользователь просит провести анализ, исследование"
            " темы или сгенерировать новые идеи. Он не предназначен для простого поиска фактов.\n"
            "Режим fast выбирай только когда ответ уже есть в истории чата, а текущий запрос —"
            " уточнение, правка или простой вопрос, ответ на который явно содержится в предыдущих"
            " сообщениях."
        ),
    ]

    prompt.add_user("\n\n".join(user_sections))

    return prompt
