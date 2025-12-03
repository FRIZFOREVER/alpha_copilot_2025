from pydantic import BaseModel, Field


class ThinkingPlan(BaseModel):
    thought: str = Field(description="Краткое обоснование следующего шага")
    query: str = Field(description="Поисковый запрос для инструмента web_search")
