from typing import Dict, Any
from ml.agent.graph.state import GraphState
from ml.agent.tools.registry import get_tool_registry
import logging

logger = logging.getLogger(__name__)


def execute_tools_node(state: GraphState) -> GraphState:
    """Execute tools based on tool_results."""
    
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
                logger.warning("web_search tool not found in registry")
                continue
            
            # Execute search
            result = tool.execute(query=query)
            
            # Store result
            executed_results.append({
                "type": "search_result",
                "data": result.data if result.success else {"error": result.error},
                "success": result.success
            })
            
            # Also add to search history
            state.search_history.append({
                "query": query,
                "success": result.success,
                "result_count": len(result.data.get("results", [])) if result.success else 0
            })
    
    # Combine existing results with new results
    state.tool_results = existing_results + executed_results
    state.research_iteration += 1
    
    return state

