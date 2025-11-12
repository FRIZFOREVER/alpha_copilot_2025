import logging
from typing import Dict

from ml.agent.graph.state import GraphState
from ml.agent.tools.registry import get_tool_registry
from ml.agent.graph.logging_utils import log_pipeline_event


def execute_tools_node(state: GraphState) -> GraphState:
    """Execute tools based on tool_results."""

    log_pipeline_event(
        "node.enter",
        state=state,
        extra={
            "node": "execute_tools",
            "pending_requests": len(state.tool_results),
        },
    )

    registry = get_tool_registry()
    executed_results = []
    
    # Keep existing search results (from previous iterations)
    existing_results = [
        r for r in state.tool_results 
        if r.get("type") == "search_result"
    ]
    
    # Process tool requests (queries)
    for tool_request in state.tool_results:
        if tool_request.get("type") == "search_query":
            query = tool_request.get("query")
            if not query:
                continue

            # Get web_search tool
            tool = registry.get("web_search")
            if not tool:
                log_pipeline_event(
                    "tools.missing_tool",
                    state=state,
                    level=logging.WARNING,
                    extra={"node": "execute_tools", "tool_name": "web_search"},
                )
                continue

            log_pipeline_event(
                "tools.query_issued",
                state=state,
                extra={"node": "execute_tools", "query": query},
            )

            # Execute search
            result = tool.execute(query=query)

            # Store result
            executed_results.append({
                "type": "search_result",
                "data": result.data if result.success else {"error": result.error},
                "success": result.success
            })

            result_count = 0
            error_message = None
            if result.success:
                result_count = len(result.data.get("results", []))
            else:
                error_message = result.error

            log_pipeline_event(
                "tools.query_result",
                state=state,
                extra={
                    "node": "execute_tools",
                    "query": query,
                    "success": result.success,
                    "result_count": result_count,
                    "error": error_message,
                },
            )

            # Also add to search history
            state.search_history.append({
                "query": query,
                "success": result.success,
                "result_count": len(result.data.get("results", [])) if result.success else 0
            })

            log_pipeline_event(
                "tools.history_recorded",
                state=state,
                extra={
                    "node": "execute_tools",
                    "query": query,
                    "success": result.success,
                    "result_count": state.search_history[-1]["result_count"],
                },
            )

    # Combine existing results with new results
    state.tool_results = existing_results + executed_results
    state.research_iteration += 1

    log_pipeline_event(
        "tools.execution_complete",
        state=state,
        extra={
            "node": "execute_tools",
            "total_results": len(state.tool_results),
            "iteration": state.research_iteration,
        },
    )

    return state

