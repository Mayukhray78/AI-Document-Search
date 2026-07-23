from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

service = DocumentService()


@router.post(
    "/upload",
    response_model=DocumentResponse,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:
        return service.upload(
            db=db,
            file=file,
            user_id=current_user.id,
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get(
    "/",
    response_model=list[DocumentResponse],
)
def get_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return service.get_all(
        db=db,
        user_id=current_user.id,
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:
        service.delete(
            db=db,
            document_id=document_id,
            user_id=current_user.id,
        )

        return {
            "message": "Document deleted successfully"
        }

    except Exception as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )