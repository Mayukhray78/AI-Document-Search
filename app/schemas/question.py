from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
    )


class QuestionResponse(BaseModel):
    question: str
    answer: str
    retrieved_chunks: list[str]