import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.document import router as document_router
from app.api.rag import router as rag_router
from app.db.database import Base, engine
from app.models import Document, User


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)

logger = logging.getLogger(__name__)

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="AI Document Search Platform",
    description=(
        "Backend API for AI-powered document search "
        "using FastAPI, PostgreSQL, Qdrant, and RAG"
    ),
    version="1.0.0",
)

frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

allowed_origins = {
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(document_router)
app.include_router(rag_router)


@app.get("/")
def home():
    return {
        "message": (
            "Welcome to AI Document Search Platform"
        ),
        "status": "Running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "Healthy"
    }


@app.on_event("startup")
def startup_event():
    logger.info(
        "AI Document Search Platform started"
    )