from fastapi import APIRouter, Depends

from app.ai.rag import RAGService
from app.core.auth import get_current_user
from app.schemas.question import (
    QuestionRequest,
    QuestionResponse,
)


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)

service = RAGService()


@router.post(
    "/ask",
    response_model=QuestionResponse,
)
def ask(
    request: QuestionRequest,
    current_user=Depends(get_current_user),
) -> QuestionResponse:

    result = service.answer(
        question=request.question,
        user_id=current_user.id,
    )

    return QuestionResponse(**result)