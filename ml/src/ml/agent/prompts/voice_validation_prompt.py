from ml.configs.message import ChatHistory, Message
from pydantic import BaseModel

class VoiceValidationResponse(BaseModel):
    voice_is_valid: bool

def get_voice_validation_prompt(message: Message) -> tuple[ChatHistory, type[VoiceValidationResponse]]:
    prompt: ChatHistory = ChatHistory()
    prompt.add_or_change_system(
        ("Ты ассистент, который должен определить, имеет ли смысл расшифровка голосового запроса пользователя\n",
        "Ответь нет, только если считаешь, что обработать текст в расшифровке НЕВОЗМОЖНО\n",
        "Если текст расшифрован на слова, но они имеет мало смысла вместе, то считай расшифровку корректной")
    )
    prompt.add_user(
        f"Расшифровка: {message.content}"
    )

    return prompt, VoiceValidationResponse