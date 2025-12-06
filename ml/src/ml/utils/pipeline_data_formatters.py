import logging
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from ml.domain.models import Evidence, ToolResult, UserProfile

logger = logging.getLogger(__name__)


def get_system_prompt(profile: "UserProfile", evidence: Sequence["Evidence"] | None = None) -> str:
    """
    Creates general system prompt for final answer as a string
    """

    sections: list[str] = []

    # Base assistant role
    sections.append(
        "Вы — продвинутый русскоязычный AI-бизнес-ассистент\n"
        "Ваша основная задача — помогать пользователю и выполнять его просьбы\n"
        "Общие правила общения:\n"
        "Всегда обращайтесь к пользователю на «вы» и сохраняйте уважительный, деловой тон.\n"
        "Объясняйте сложные вещи простым языком, по шагам, с конкретными примерами.\n"
        "прямо говорите об этом и предлагайте, какие данные пользователь может вам дать."
    )

    # User information
    user_meta_parts: list[str] = []

    if profile.username:
        user_meta_parts.append(f"Полное имя пользователя (ФИО): {profile.username}.\n")
        user_meta_parts.append(
            "Если вы хотите обратиться к пользователю по имени, используйте уважительную форму "
            "«имя + отчество» (например: «Иван Петрович») и обязательно обращайтесь на «вы»."
        )

    if profile.user_info:
        user_meta_parts.append(
            f"\nКраткое описание пользователя (его собственные слова):\n{profile.user_info}"
        )

    if user_meta_parts:
        sections.append("Информация о пользователе:\n" + "\n".join(user_meta_parts))

    # Business information
    if profile.business_info:
        sections.append(
            "Информация о бизнесе пользователя (описание от пользователя):\n"
            f"{profile.business_info}\n\n"
            "Используйте эти данные, чтобы адаптировать рекомендации под его нужды, но"
            " не основывайте ваш ответ на них"
        )

    # Additional instructions
    if profile.additional_instructions:
        sections.append(
            "Дополнительные инструкции, заданные пользователем для ассистента:\n"
            f"{profile.additional_instructions}\n\n"
            "Эти инструкции имеют высокий приоритет. Если они не противоречат базовым "
            "системным правилам, строго им следуйте."
        )
    else:
        sections.append(
            "Если дополнительных инструкций от пользователя нет, действуйте по своим "
            "базовым правилам: будьте вежливы, полезны, структурируйте ответы, "
            "давайте практичные и реалистичные рекомендации."
        )

    # Dialogue behavior
    sections.append(
        "Поведение в диалоге:\n"
        "Для сложных задач предлагайте пошаговый план действий.\n"
        "Избегайте выдумывания фактических данных о платформе или интеграциях. "
        "Если чего-то не знаете, честно скажите об этом и предложите общий подход. "
        "В первую очередь постарайся ответить на запрос пользователя\n"
        "Не вставляй в ответе ссылки на файлы или их названия, даже если ты их сгенерировал\n"
        "Это произойдёт автоматически и пользователь увидит твой результат работы.\n"
        "В таком случае просто напиши пользователю об успешном выполнении задания"
    )

    if evidence is not None:
        evidence_text = format_research_observations(evidence)
        evidence_section = (
            "Доступных материалов из загруженных файлов или поиска нет."
            if not evidence_text
            else (
                "Полагайся на проверенные материалы ниже.\n"
                "Эти данные получены из файлов или веб-поиска:\n"
                f"{evidence_text}"
            )
        )
        sections.append(evidence_section)

    system_prompt: str = "\n\n".join(sections)
    return system_prompt


def format_research_observations(observations: Sequence["Evidence"]) -> str:
    formatted: list[str] = []
    for index, observation in enumerate(observations, start=1):
        formatted.append(_format_evidence(index, observation))

    return "\n\n".join(formatted)


def _format_evidence(index: int, observation: "Evidence") -> str:
    tool_name = observation.tool_name
    tool_result = observation.source

    if tool_name == "file_reader":
        return _format_file_evidence(index, tool_result)

    if tool_name == "file_writer":
        return _format_created_file_evidence(index, tool_result)

    if tool_name == "web_search":
        return _format_web_evidence(index, tool_result)

    return f"{index}. Источник: инструмент {tool_name}\nДанные:\n{observation.summary}"


def _format_file_evidence(index: int, result: "ToolResult") -> str:
    data = result.data
    if not isinstance(data, str):
        raise TypeError("file_reader evidence must contain string data")

    return f"{index}. Источник: загруженный файл (tool: file_reader)\n{data}"


def _format_created_file_evidence(index: int, result: "ToolResult") -> str:
    data = result.data
    if not isinstance(data, dict):
        raise TypeError("file_writer evidence must be a dictionary")
    if "message" not in data:
        raise ValueError("file_writer evidence is missing 'message'")
    if "file_url" not in data:
        raise ValueError("file_writer evidence is missing 'file_url'")

    message = data["message"]
    file_url = data["file_url"]

    if not isinstance(message, str):
        raise TypeError("file_writer evidence 'message' must be a string")
    if not isinstance(file_url, str):
        raise TypeError("file_writer evidence 'file_url' must be a string")

    return (
        f"{index}. Источник: созданный файл (tool: file_writer)\n"
        f"{message}\n"
        f"URL файла: {file_url}"
    )


def _format_web_evidence(index: int, result: "ToolResult") -> str:
    data = result.data
    if not isinstance(data, dict):
        raise TypeError("web_search evidence must be a dictionary")
    if "query" not in data:
        raise ValueError("web_search evidence is missing 'query'")
    if "results" not in data:
        raise ValueError("web_search evidence is missing 'results'")

    query = data["query"]
    results = data["results"]

    if not isinstance(query, str):
        raise TypeError("web_search evidence 'query' must be a string")
    if not isinstance(results, list):
        raise TypeError("web_search evidence 'results' must be a list")

    formatted_results: list[str] = []
    for result_index, result_entry in enumerate(results, start=1):
        if not isinstance(result_entry, dict):
            raise TypeError("web_search evidence result entry must be a dictionary")
        if "url" not in result_entry:
            raise ValueError("web_search evidence result entry is missing 'url'")
        if "title" not in result_entry:
            raise ValueError("web_search evidence result entry is missing 'title'")
        if "content" not in result_entry:
            raise ValueError("web_search evidence result entry is missing 'content'")

        url = result_entry["url"]
        title = result_entry["title"]
        content = result_entry["content"]

        if not isinstance(url, str):
            raise TypeError("web_search evidence result 'url' must be a string")
        if not isinstance(title, str):
            raise TypeError("web_search evidence result 'title' must be a string")
        if not isinstance(content, str):
            raise TypeError("web_search evidence result 'content' must be a string")

        formatted_results.append(
            (f"- Результат {result_index}: {title}\n  URL: {url}\n  Извлечённый текст:\n{content}")
        )

    results_block = "\n".join(formatted_results)

    return (
        f"{index}. Источник: веб-поиск (tool: web_search)\n"
        f"Поисковый запрос: {query}\n"
        f"Детали результатов:\n{results_block}"
    )
