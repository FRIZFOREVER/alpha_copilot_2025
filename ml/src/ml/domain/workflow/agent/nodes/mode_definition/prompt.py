from ml.domain.models import ChatHistory, Message


async def get_mode_definition_prompt(message: Message) -> ChatHistory:
    system_prompt: str = (
        "Вы — диспетчер, выбирающий стратегию ответа (fast/thinking) для ассистента."
        "Отвечайте ТОЛЬКО одним JSON-объектом с единственным полем mode, "
        'например {"mode":"thinking"}.'
        "Thinking — основной режим для рассуждений, планов и рекомендаций; "
        "выбирайте его по умолчанию."
        "Если запрос связан с работой с файлами (открытие, чтение,"
        " редактирование или генерация содержимого), выбирайте thinking."
        "Fast допускается только когда ответ уже есть в истории, и от пользователя требуется "
        "лишь уточнение, либо запрос пользователя очень простой и не требует уточнения "
        "информации в интернете."
        "Не добавляйте пояснений, только поставьте нужный режим."
    )

    prompt = ChatHistory()
    prompt.add_or_change_system(system_prompt)
    prompt.add_user(message)

    return prompt
