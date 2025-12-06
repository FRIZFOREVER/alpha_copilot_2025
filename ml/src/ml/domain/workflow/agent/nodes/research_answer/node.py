import logging

from ml.domain.models import ChatHistory, GraphState
from ml.domain.workflow.agent.tools.final_answer.tool import FinalAnswerTool
from ml.utils import format_research_observations

logger = logging.getLogger(__name__)


async def research_answer(state: GraphState) -> GraphState:
    logger.info("Entering research_answer node")

    tool = FinalAnswerTool()
    result = await tool.execute(
        chat=state.chat, profile=state.user, evidence=state.evidence_list
    )

    if not isinstance(result.data, dict):
        raise ValueError("Final answer tool result must be a dictionary")

    final_prompt = result.data.get("final_prompt")
    if not isinstance(final_prompt, ChatHistory):
        raise ValueError("Final prompt missing or invalid in final answer tool result")

    observations_text = format_research_observations(state.evidence_list)
    user_request = state.chat.last_message().content

    details_prefix = "Research observations:"
    observations_suffix = observations_text if observations_text else "none collected"

    final_prompt.add_user(
        f"{details_prefix}\n{observations_suffix}\nOriginal request: {user_request}"
    )

    state.final_prompt = final_prompt
    state.pending_tool_call = None

    return state
