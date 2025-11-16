import logging

from ml.agent.graph.state import GraphState
from ml.agent.prompts import (
    ModeDecisionResponse,
    get_mode_decision_prompt,
    summarize_conversation_for_observer,
)
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ModelMode

logger: logging.Logger = logging.getLogger(__name__)


def graph_mode_node(state: GraphState, *, client: ReasoningModelClient) -> GraphState:
    logger.info("Entered Graph mode node")
    if state.payload.mode == ModelMode.Auto:
        conversation_summary = summarize_conversation_for_observer(state.payload.messages)
        evidence: list[str] = []
        evidence.extend(state.thinking_evidence)
        evidence.extend(state.final_answer_evidence)
        evidence.extend(state.memories.extracted_memories)

        prompt = get_mode_decision_prompt(
            profile=state.payload.profile,
            conversation_summary=conversation_summary,
            tag=state.payload.tag,
            evidence=evidence,
        )
        try:
            decision: ModeDecisionResponse = client.call_structured(
                prompt,
                ModeDecisionResponse,
            )
        except Exception:
            logger.exception("Failed to select mode via structured call")
            raise

        state.payload.mode = decision.mode
        logger.info("Mode selected dynamically: %s", state.payload.mode.value)

    return state
