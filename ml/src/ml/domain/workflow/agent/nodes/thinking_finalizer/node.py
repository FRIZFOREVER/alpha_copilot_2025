import logging

from ml.domain.models import ChatHistory, GraphState
from ml.domain.workflow.agent.tools.final_answer.tool import FinalAnswerTool

logger = logging.getLogger(__name__)


async def thinking_finalize(state: GraphState) -> GraphState:
    logger.info("Entering thinking_finalize node")

    final_answer_tool = FinalAnswerTool()
    result = await final_answer_tool.execute(
        chat=state.chat,
        profile=state.user,
        evidence=state.evidence_list,
    )

    if not isinstance(result.data, dict):
        raise TypeError("Final answer tool returned unexpected data type")
    if "final_prompt" not in result.data:
        raise KeyError("Final answer tool result missing 'final_prompt'")

    final_prompt = result.data["final_prompt"]
    if not isinstance(final_prompt, ChatHistory):
        raise TypeError("Final prompt must be an instance of ChatHistory")

    state.final_prompt = final_prompt

    return state
