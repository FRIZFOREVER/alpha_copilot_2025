from enum import Enum

from pydantic import BaseModel

from ml.domain.models import ModelMode


class ModeDecisionChoice(str, Enum):
    Fast = ModelMode.Fast.value
    Thinking = ModelMode.Thiking.value


class ModeDecisionResponse(BaseModel):
    mode: ModeDecisionChoice
