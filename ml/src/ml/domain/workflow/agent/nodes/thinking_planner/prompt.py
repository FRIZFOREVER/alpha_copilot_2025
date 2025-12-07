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


def get_thinking_plan_prompt(
    chat: ChatHistory,
    profile: UserProfile,
    available_tools: dict[str, BaseTool],
    evidence_list: list[Evidence],
    remaining_steps: int,
) -> ChatHistory:
    system_prompt_parts: list[str] = [get_system_prompt(profile)]

    evidence_block = (
        "Наблюдений пока нет." if not evidence_list else format_research_observations(evidence_list)
    )

    planning_instructions = (
        "Ты выполняешь один шаг размышления и выбираешь следующий инструмент.\n"
        "Если готов дать ответ, выбери инструмент final_answer.\n"
        "Доступные инструменты:\n"
        f"{_format_available_tools(available_tools)}\n"
        "Всегда возвращай JSON с полями thought, chosen_tool, tool_args.\n"
        "Если пользователь просит создать или заполнить файл, обязательно выбери инструмент"
        " создания файла до final_answer.\n"
        "Не считай примеры из истории диалога готовыми файлами — пропускай создание файла"
        " только если файл реально уже записан в этом диалоге.\n"
        "Учти текущие наблюдения — каждый пункт содержит источник (tool_name => результат).\n"
        f"Текущие наблюдения:\n{evidence_block}\n"
        f"Осталось шагов до обязательного завершения: {remaining_steps}."
    )

    system_prompt_parts.append(planning_instructions)
    system_message = "\n\n".join(system_prompt_parts)

    prompt = ChatHistory(messages=list(chat.messages))
    prompt.add_or_change_system(system_message)

    return prompt
