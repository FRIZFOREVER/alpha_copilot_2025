from ml.domain.models import ChatHistory, UserProfile
from ml.domain.models.tools_data import Evidence
from ml.domain.workflow.agent.tools import BaseTool
from ml.utils import format_research_observations, get_system_prompt


def _format_available_tools(available_tools: dict[str, BaseTool]) -> str:
    tool_lines: list[str] = []
    for tool in available_tools.values():
        tool_lines.append(
            "- {name}: {description}. Schema: {schema}".format(
                name=tool.name, description=tool.description, schema=tool.schema
            )
        )
    return "\n".join(tool_lines)


def get_research_reason_prompt(
    chat: ChatHistory,
    profile: UserProfile,
    available_tools: dict[str, BaseTool],
    evidence_list: list[Evidence],
) -> ChatHistory:
    system_sections: list[str] = [get_system_prompt(profile)]

    available_tools_text = _format_available_tools(available_tools)

    evidence_block = (
        "Наблюдений пока нет." if not evidence_list else format_research_observations(evidence_list)
    )

    reasoning_instructions = (
        "Ты управляешь исследовательским циклом с инструментами.\n"
        "Используй доступные инструменты, чтобы получить факты и затем сформировать финальный ответ.\n"
        "Выбери один инструмент, который нужно вызвать следующим.\n"
        "Всегда возвращай JSON со следующими полями: thought, chosen_tool, tool_args.\n"
        "Если готов отвечать пользователю, выбирай инструмент final_answer.\n"
        f"Доступные инструменты:\n{available_tools_text}\n"
        f"Текущие наблюдения:\n{evidence_block}\n"
        "Если пользователь просит подготовить файл, обязательно выбери инструмент создания файла"
        " прежде чем переходить к final_answer.\n"
        "Не считай примеры из истории диалога готовыми файлами — пропускай создание файла"
        " только если файл действительно уже записан в текущем диалоге"
    )

    system_sections.append(reasoning_instructions)

    system_message = "\n\n".join(system_sections)

    prompt = ChatHistory(messages=list(chat.messages))
    prompt.add_or_change_system(system_message)

    return prompt
