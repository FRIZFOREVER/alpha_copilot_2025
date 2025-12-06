from pydantic import BaseModel, Field


class ChunkRelevance(BaseModel):
    is_chunk_relevant: bool = Field(
        ..., description="True if the provided text chunk is useful for the search query"
    )
