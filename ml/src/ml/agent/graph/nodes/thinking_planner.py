from typing import Any

from ml.agent.graph.state import GraphState, NextAction, PlannerToolExecution
from ml.agent.prompts import (
    ThinkingPlannerStructuredOutput,
    get_thinking_planner_prompt,
)
from ml.agent.tools.registry import get_tool_registry
from ml.api.ollama_calls import ReasoningModelClient


def _summarize_payload(payload: Any) -> str:
    text = str(payload)
    max_length = 600
    if len(text) > max_length:
        return text[:max_length]
    return text


def thinking_planner_node(state: GraphState, client: ReasoningModelClient) -> GraphState:
    registry = get_tool_registry()
    prompt = get_thinking_planner_prompt(
        system_prompt=state.payload.system,
        conversation=state.payload.messages,
        memories=state.memories.extracted_memories,
        available_tools=list(registry.values()),
        max_actions=2,
    )

    structured_plan: ThinkingPlannerStructuredOutput = client.call_structured(
        prompt,
        ThinkingPlannerStructuredOutput,
    )

    state.thinking_plan_summary = structured_plan.plan_summary
    state.thinking_plan_steps = structured_plan.plan_steps
    state.final_answer_draft = structured_plan.final_draft

    executed: list[PlannerToolExecution] = []
    gathered_evidence: list[str] = []
    used_tools: set[str] = set()

    for call in structured_plan.tool_calls:
        if len(used_tools) >= 2:
            break
        tool_name = call.tool_name
        if tool_name in used_tools:
            continue
        tool = registry.get(tool_name)
        if tool is None:
            continue

        used_tools.add(tool_name)
        result = tool.execute(**call.arguments)

        preview = ""
        if result.success:
            preview = _summarize_payload(result.data)
            evidence_note = call.expected_evidence
            if evidence_note and preview:
                gathered_evidence.append(evidence_note + "\n" + preview)
            elif preview:
                gathered_evidence.append(preview)
        else:
            error_text = result.error
            if error_text:
                preview = error_text

        executed.append(
            PlannerToolExecution(
                tool_name=tool_name,
                arguments=call.arguments,
                success=result.success,
                output_preview=preview,
            )
        )

    state.thinking_tool_executions = executed
    state.thinking_evidence = gathered_evidence
    if gathered_evidence:
        state.final_answer_evidence = list(gathered_evidence)

    state.next_action = NextAction.ANSWER
    return state
