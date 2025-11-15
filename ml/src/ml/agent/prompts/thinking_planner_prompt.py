"""Prompt builder and structured schema for the thinking planner stage."""

from collections.abc import Sequence

from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory
from pydantic import BaseModel, Field, model_validator


class PlannerToolCall(BaseModel):
    """Structured description of a single planner tool call."""

    tool_name: str = Field(
        description="Exact registry name of the tool to execute",
    )
    arguments: dict[str, str] = Field(
        default_factory=dict,
        description="Keyword arguments that should be passed to the tool",
    )
    rationale: str = Field(
        default="",
        description="Why this tool helps to progress the plan",
    )
    expected_evidence: str = Field(
        default="",
        description="What evidence the planner expects to extract",
    )


class ThinkingPlannerStructuredOutput(BaseModel):
    """Structured response emitted by the thinking planner."""

    plan_summary: str = Field(
        description="One paragraph recap of the overall solution strategy",
    )
    plan_steps: list[str] = Field(
        default_factory=list,
        description="Ordered bullet list explaining the upcoming steps",
    )
    tool_calls: list[PlannerToolCall] = Field(
        default_factory=list,
        description="Tool invocations that should be executed sequentially",
    )
    final_draft: str = Field(
        description="Draft of the final assistant answer after applying the plan",
    )

    @model_validator(mode="after")
    def _validate_tool_usage(self) -> "ThinkingPlannerStructuredOutput":
        tool_names: list[str] = []
        for call in self.tool_calls:
            tool_names.append(call.tool_name)
        unique_names: set[str] = set()
        for name in tool_names:
            if name in unique_names:
                raise ValueError("Каждый инструмент может использоваться только один раз")
            unique_names.add(name)
        if len(tool_names) > 2:
            raise ValueError("Можно запланировать не более двух инструментов")
        return self


def _format_tool_catalog(tools: Sequence[BaseTool]) -> str:
    if not tools:
        return "Нет доступных инструментов"
    lines: list[str] = []
    for tool in tools:
        description = tool.description
        schema = tool.schema
        schema_text = str(schema)
        lines.append(
            "Название: "
            + tool.name
            + "\nОписание: "
            + description
            + "\nСхема аргументов: "
            + schema_text
        )
    return "\n\n".join(lines)


def _format_plan_guidelines(max_actions: int) -> str:
    points: list[str] = []
    points.append(
        "Сформируй краткий сводный план решения задачи, затем предложи пошаговую стратегию."
    )
    points.append(
        "Рассмотри использование инструментов только если они критически необходимы для получения фактов."
    )
    points.append(
        "Можно запланировать максимум " + str(max_actions) + " действия с инструментами, "
        "и каждый инструмент можно использовать не более одного раза."
    )
    points.append("Если инструменты не нужны, оставь список вызовов пустым и объясни почему.")
    points.append("В финальном черновике дай развернутый ответ, ссылаясь на собранные факты.")
    return "\n".join(points)


def get_thinking_planner_prompt(
    *,
    system_prompt: str,
    conversation: ChatHistory,
    memories: Sequence[str],
    available_tools: Sequence[BaseTool],
    max_actions: int = 2,
) -> ChatHistory:
    """Build the prompt that instructs the planner to return structured output."""

    prompt = ChatHistory()
    planner_instructions: list[str] = []
    planner_instructions.append(system_prompt)
    planner_instructions.append(
        "Ты отвечаешь за построение плана рассуждений и выбора инструментов."
    )
    planner_instructions.append(
        "Всегда следуй требуемой структуре JSON и выполняй ограничения на использование инструментов."
    )
    prompt.add_or_change_system("\n".join(planner_instructions))

    user_sections: list[str] = []
    conversation_dump = conversation.model_dump_string()
    if conversation_dump:
        user_sections.append("Контекст диалога:\n" + conversation_dump)
    else:
        user_sections.append("Контекст диалога:\nнет сообщений")

    if memories:
        user_sections.append("Извлеченные заметки:\n" + "\n".join(memories))

    tool_catalog = _format_tool_catalog(available_tools)
    user_sections.append("Каталог инструментов:\n" + tool_catalog)

    guidelines = _format_plan_guidelines(max_actions)
    user_sections.append("Правила построения плана:\n" + guidelines)

    user_sections.append(
        "Верни JSON со следующими полями: plan_summary (строка), plan_steps (список строк), "
        "tool_calls (список объектов с полями tool_name, arguments, rationale, expected_evidence), "
        "final_draft (строка)."
    )

    prompt.add_user("\n\n".join(user_sections))
    return prompt
