from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.session import get_db
from app.main import app


test_engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

Base.metadata.create_all(
    bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "api-test@example.com",
            "password": "SecurePassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == "api-test@example.com"
    assert "password" not in data


def test_login_user():
    response = client.post(
        "/auth/login",
        json={
            "email": "api-test@example.com",
            "password": "SecurePassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "api-test@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid email or password"
    )