from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.db.session import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

service = AuthService()


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return service.register(
            db=db,
            name=user.name,
            email=user.email,
            password=user.password
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        return service.login(
            db=db,
            email=user.email,
            password=user.password
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )