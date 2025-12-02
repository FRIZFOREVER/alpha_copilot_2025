from ml.domain.models import ChatHistory, Message


def get_voice_validation_prompt(message: Message) -> ChatHistory:
    prompt: ChatHistory = ChatHistory()

    prompt.add_user(message)

    prompt.add_or_change_system(
        "Ты ассистент, который должен определить, имеет ли смысл расшифровка голосового "
        "запроса пользователя\n"
        "Ответь нет, только если считаешь, что адекватно обработать текст в расшифровке НЕВОЗМОЖНО\n"
        "Если текст расшифрован на слова, но они имеет мало смысла вместе, то считай расшифровку "
        "корректной"
    )

    return prompt
