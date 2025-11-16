"""Prompt builder and structured schema for the thinking planner stage."""

from collections.abc import Sequence

from ml.agent.prompts.context_blocks import (
    build_conversation_context_block,
    build_persona_block,
)
from ml.agent.tools.base import BaseTool
from ml.configs.message import ChatHistory, UserProfile
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
        "Отвечай только на основании проверенных фактов: если нужных данных нет в контексте,"
        " обязательно запланируй инструмент, чтобы собрать свежие доказательства."
    )
    points.append(
        "Если пользователь просит что-либо найти в интернете, назвать источник или ссылку,"
        " обязательно добавь вызов web_search с релевантным запросом."
    )
    points.append(
        "Можно запланировать максимум " + str(max_actions) + " действия с инструментами, "
        "и каждый инструмент можно использовать не более одного раза."
    )
    points.append("Если инструменты не нужны, оставь список вызовов пустым и объясни почему.")
    points.append("В финальном черновике дай развернутый ответ, ссылаясь на собранные факты.")
    return "\n".join(points)


def _format_memories(memories: Sequence[str]) -> str:
    numbered: list[str] = []
    for index, memory in enumerate(memories, start=1):
        numbered.append(str(index) + ". " + memory)
    return "Извлеченные заметки:\n" + "\n".join(numbered)


def _format_evidence(evidence_snippets: Sequence[str]) -> str:
    formatted: list[str] = []
    for position, snippet in enumerate(evidence_snippets, start=1):
        formatted.append("[" + str(position) + "] " + snippet)
    return "Доступные факты из предыдущих действий:\n" + "\n".join(formatted)


def get_thinking_planner_prompt(
    *,
    profile: UserProfile,
    conversation: ChatHistory,
    memories: Sequence[str],
    evidence_snippets: Sequence[str] | None,
    available_tools: Sequence[BaseTool],
    max_actions: int = 2,
) -> ChatHistory:
    """Build the prompt that instructs the planner to return structured output."""

    prompt = ChatHistory()
    planner_instructions: list[str] = []
    persona_block = build_persona_block(profile)
    conversation_block = build_conversation_context_block(conversation)

    system_sections: list[str] = []
    system_sections.append(persona_block)
    if conversation_block:
        system_sections.append(conversation_block)

    if evidence_snippets:
        evidence_block = _format_evidence(evidence_snippets)
        system_sections.append(evidence_block)

    if memories:
        memories_block = _format_memories(memories)
        system_sections.append(memories_block)

    tool_catalog = _format_tool_catalog(available_tools)
    system_sections.append("Каталог инструментов:\n" + tool_catalog)

    guidelines = _format_plan_guidelines(max_actions)
    system_sections.append("Правила построения плана:\n" + guidelines)

    planner_instructions.append(
        "Ты отвечаешь за построение плана рассуждений и выбора инструментов."
    )
    planner_instructions.append(
        "Всегда следуй требуемой структуре JSON и выполняй ограничения на использование инструментов."
    )
    planner_block = "Инструкции планировщика:\n" + "\n".join(planner_instructions)
    system_sections.append(planner_block)

    prompt.add_or_change_system("\n\n".join(system_sections))

    prompt.add_user(
        "Верни JSON со следующими полями: plan_summary (строка), plan_steps (список строк), "
        "tool_calls (список объектов с полями tool_name, arguments, rationale, expected_evidence), "
        "final_draft (строка)."
    )
    return prompt
