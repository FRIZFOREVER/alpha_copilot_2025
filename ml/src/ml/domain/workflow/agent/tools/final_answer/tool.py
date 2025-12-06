from typing import Any, Sequence

from ml.domain.models import ChatHistory, UserProfile
from ml.domain.models.tools_data import Evidence, ToolResult
from ml.domain.workflow.agent.tools.base_tool import BaseTool
from ml.utils import format_research_observations, get_system_prompt


class FinalAnswerTool(BaseTool):
    """Tool that prepares the final prompt for streaming answer generation."""

    @property
    def name(self) -> str:
        return "final_answer"

    @property
    def description(self) -> str:
        return "Формирует финальный промпт с учетом собранных наблюдений."

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "answer_hint": {
                    "type": "string",
                    "description": "Необязательный предварительный ответ или ключевые пункты.",
                }
            },
        }

    async def execute(
        self,
        *,
        chat: ChatHistory,
        profile: UserProfile,
        evidence: Sequence[Evidence],
        answer_hint: str | None = None,
    ) -> ToolResult:
        final_chat = ChatHistory(messages=list(chat.messages))
        system_prompt = get_system_prompt(profile)
        final_chat.add_or_change_system(system_prompt)

        evidence_text = format_research_observations(evidence)
        evidence_prefix = "Собранные наблюдения отсутствуют." if not evidence_text else "Собранные наблюдения:\n"
        final_chat.add_assistant(f"{evidence_prefix}{evidence_text}")

        if answer_hint:
            final_chat.add_assistant(
                "Рекомендуемый ответ или важные пункты, которые нужно раскрыть:\n"
                f"{answer_hint}"
            )

        return ToolResult(success=True, data={"final_prompt": final_chat})
