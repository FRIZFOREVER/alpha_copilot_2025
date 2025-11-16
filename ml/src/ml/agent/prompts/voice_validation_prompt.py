from pydantic import BaseModel

from ml.configs.message import ChatHistory


class VoiceValidationResponse(BaseModel):
    voice_is_valid: bool


def get_voice_validation_prompt(
    message: ChatHistory,
) -> tuple[ChatHistory, type[VoiceValidationResponse]]:
    message.add_or_change_system(
        "Ты ассистент, который должен определить, имеет ли смысл расшифровка голосового "
        "запроса пользователя\n"
        "Ответь нет, только если считаешь, что обработать текст в расшифровке НЕВОЗМОЖНО\n"
        "Если текст расшифрован на слова, но они имеет мало смысла вместе, то считай расшифровку "
        "корректной"
    )

    return message, VoiceValidationResponse
