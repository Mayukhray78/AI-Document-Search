from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token


def test_password_hashing():
    password = "SecurePassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True
    assert verify_password("WrongPassword", hashed_password) is False


def test_access_token_creation():
    token = create_access_token(
        data={"sub": "test@example.com"}
    )

    assert isinstance(token, str)
    assert len(token) > 0