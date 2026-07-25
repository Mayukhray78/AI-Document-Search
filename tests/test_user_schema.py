import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserLogin


def test_valid_user_registration():
    user = UserCreate(
        name="Test User",
        email="test@example.com",
        password="SecurePassword123",
    )

    assert user.name == "Test User"
    assert user.email == "test@example.com"


def test_invalid_email_registration():
    with pytest.raises(ValidationError):
        UserCreate(
            name="Test User",
            email="invalid-email",
            password="SecurePassword123",
        )


def test_valid_user_login():
    user = UserLogin(
        email="test@example.com",
        password="SecurePassword123",
    )

    assert user.email == "test@example.com"