from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token

repo = UserRepository()


class AuthService:

    def register(self, db: Session, name: str, email: str, password: str):

        existing_user = repo.get_by_email(db, email)

        if existing_user:
            raise Exception("Email already exists")

        hashed_password = hash_password(password)

        return repo.create(
            db=db,
            name=name,
            email=email,
            password=hashed_password
        )

    def login(self, db: Session, email: str, password: str):

        user = repo.get_by_email(db, email)

        if not user:
            raise Exception("Invalid email or password")

        if not verify_password(password, user.password):
            raise Exception("Invalid email or password")

        access_token = create_access_token(
            data={"sub": user.email}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }