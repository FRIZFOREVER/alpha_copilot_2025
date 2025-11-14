from pydantic import BaseModel
import logging
from ml.agent.prompts import get_tag_define_prompt
from ml.api.ollama_calls import ReasoningModelClient
from ml.configs.message import ChatHistory, Tag

logger = logging.getLogger(__name__)

class DefinedTag(BaseModel):
    tag: Tag


def define_tag(
    last_message: ChatHistory, reasoning_client: ReasoningModelClient
) -> Tag:
    """Makes a structured output call to reasoning client"""
    last_message.add_or_change_system(get_tag_define_prompt())
    tag: DefinedTag = reasoning_client.call_structured(
        messages=last_message, 
        output_schema=DefinedTag
    )
    return tag.tag
