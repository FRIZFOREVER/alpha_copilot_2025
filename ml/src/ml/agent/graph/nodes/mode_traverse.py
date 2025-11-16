import logging

from ml.agent.graph.state import GraphState
from ml.agent.prompts import ModeDecisionResponse, get_mode_decision_prompt
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ModelMode

logger: logging.Logger = logging.getLogger(__name__)


def graph_mode_node(state: GraphState, *, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Graph mode node")
    if state.payload.mode == ModelMode.Auto:
        logger.info("Running dynamic mode selection via the latest user request")

        prompt_history = state.payload.messages.last_message_as_history()
        prompt = get_mode_decision_prompt(
            profile=state.payload.profile,
            history=prompt_history,
        )
        try:
            decision: ModeDecisionResponse = client.call_structured(
                prompt,
                ModeDecisionResponse,
            )
        except Exception:
            logger.exception("Failed to select mode via structured call")
            raise

        try:
            state.payload.mode = ModelMode(decision.mode.value)
        except ValueError:
            logger.exception("Failed to coerce mode decision into ModelMode: %s", decision.mode)
            raise
        logger.info("Mode selected dynamically: %s", state.payload.mode.value)

    return state
