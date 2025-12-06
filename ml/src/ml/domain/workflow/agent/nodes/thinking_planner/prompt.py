from ml.domain.models import ChatHistory, UserProfile
from ml.utils import get_system_prompt


def get_thinking_plan_prompt(chat: ChatHistory, profile: UserProfile) -> ChatHistory:
    system_prompt_parts: list[str] = [get_system_prompt(profile)]

    planning_instructions = (
        "Вы выполняете один шаг размышления с помощью инструмента web_search.\n"
        "Найдите формулировку поискового запроса, которая поможет ответить на последнюю "
        "просьбу пользователя.\n"
        "Доступный инструмент: web_search с параметром query (string).\n"
        "Верните JSON со свойствами thought и query.\n"
        "thought — краткое обоснование поиска. query — поисковый запрос, который нужно "
        "выполнить.\n"
        "Не вызывайте инструмент, только сформируйте запрос."
    )

    system_prompt_parts.append(planning_instructions)
    system_message = "\n\n".join(system_prompt_parts)

    prompt = ChatHistory(messages=list(chat.messages))
    prompt.add_or_change_system(system_message)

    return prompt
