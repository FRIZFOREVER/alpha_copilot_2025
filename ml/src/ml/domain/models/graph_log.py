from enum import Enum
from typing import TypedDict


class PicsTags(str, Enum):
    Web = "web"
    Think = "think"
    Mic = "mic"
    Tool = "tool"


class GraphLogMessage(TypedDict):
    tag: PicsTags
    answer_id: int
    message: str
