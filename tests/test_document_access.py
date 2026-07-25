import pytest
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


@pytest.fixture(scope="module")
def access_token():
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Document Test User",
            "email": "document-test@example.com",
            "password": "SecurePassword123",
        },
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": "document-test@example.com",
            "password": "SecurePassword123",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def test_documents_require_authentication():
    response = client.get("/documents/")

    assert response.status_code in (401, 403)


def test_authenticated_user_can_list_documents(
    access_token,
):
    response = client.get(
        "/documents/",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_delete_missing_document(
    access_token,
):
    response = client.delete(
        "/documents/999999",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            )
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Document not found or access denied"
    )