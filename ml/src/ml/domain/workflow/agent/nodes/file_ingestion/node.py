import logging

from ml.api.external import send_graph_log
from ml.domain.models import Evidence, GraphState, ToolResult
from ml.domain.models.graph_log import PicsTags
from ml.domain.workflow.agent.tools.file_reader.tool import FileReaderTool

logger = logging.getLogger(__name__)


async def ingest_file(state: GraphState) -> GraphState:
    logger.info("Entering ingest_file node")

    file_url = state.file_url
    if file_url is None:
        logger.info("No file URL provided; skipping file ingestion")
        return state

    if not isinstance(file_url, str):
        raise TypeError("GraphState.file_url must be a string when provided")

    if file_url == "":
        logger.info("Empty file URL provided; skipping file ingestion")
        return state

    tool = FileReaderTool()
    answer_id = state.chat.last_user_message_id()
    await send_graph_log(
        chat_id=state.chat_id,
        tag=PicsTags.Tool,
        message="Чтение файла",
        answer_id=answer_id,
    )
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
