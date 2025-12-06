import logging

from ml.domain.models import Evidence, GraphState, ToolResult
from ml.domain.workflow.agent.tools.file_reader.tool import FileReaderTool

logger = logging.getLogger(__name__)


async def ingest_file(state: GraphState) -> GraphState:
    logger.info("Entering ingest_file node")

    file_url = state.file_url
    if file_url is None:
        return state

    tool = FileReaderTool()
    try:
        result: ToolResult = await tool.execute(file_url=file_url)
    except Exception as exc:
        logger.exception("File reader tool execution failed")
        failure_message = f"Не удалось прочитать файл: {exc}"
        result = ToolResult(success=False, data=failure_message, error=str(exc))

    observation = Evidence(tool_name=tool.name, summary=str(result.data), source=result)
    state.evidence_list.append(observation)
    state.last_tool_result = result
    state.last_executed_tool = tool.name

    return state
