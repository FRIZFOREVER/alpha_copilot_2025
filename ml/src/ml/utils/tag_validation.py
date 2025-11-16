import logging

from ml.agent.prompts import get_tag_define_prompt
from ml.api.graph_history import PicsTags
from ml.api.graph_logging import send_graph_log
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory, Tag
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DefinedTag(BaseModel):
    tag: Tag


def define_tag(
    last_message: ChatHistory,
    reasoning_client: ReasoningModelClient,
    answer_id: int | None = None,
) -> Tag:
    """Makes a structured output call to reasoning client"""
    if not send_graph_log(PicsTags.Think, answer_id, "Определяю тему"):
        logger.debug("Graph log dispatcher unavailable for tag definition start")
    last_message.add_or_change_system(get_tag_define_prompt())
    tag: DefinedTag = reasoning_client.call_structured(
        messages=last_message, output_schema=DefinedTag
    )
    if not send_graph_log(PicsTags.Think, answer_id, f"Тема определена: {tag.tag.value}"):
        logger.debug("Graph log dispatcher unavailable for tag definition result")
    return tag.tag
