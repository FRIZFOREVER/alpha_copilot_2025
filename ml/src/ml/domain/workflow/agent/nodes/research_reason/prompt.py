from ml.domain.models import ChatHistory, UserProfile
from ml.domain.workflow.agent.tools import BaseTool


def get_research_reason_prompt(
    chat: ChatHistory, profile: UserProfile, available_tools: dict[str, BaseTool]
) -> ChatHistory: ...
