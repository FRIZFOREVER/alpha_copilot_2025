from pydantic import BaseModel

from ml.domain.models import Tag


class DefinedTag(BaseModel):
    tag: Tag
