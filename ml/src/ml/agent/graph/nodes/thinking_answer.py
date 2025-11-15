"""Finalization node for the thinking pipeline."""

from ml.agent.graph.state import GraphState, NextAction
from ml.agent.prompts import get_thinking_answer_prompt


def thinking_answer_node(state: GraphState) -> GraphState:
    prompt = get_thinking_answer_prompt(
        system_prompt=state.payload.system,
        conversation=state.payload.messages,
        plan_summary=state.thinking_plan_summary,
        plan_steps=state.thinking_plan_steps,
        evidence=state.thinking_evidence,
        draft=state.final_answer_draft or "",
    )

    state.final_prompt = prompt
    state.next_action = NextAction.FINISH
    return state
