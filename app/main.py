from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.document import router as document_router
from app.api.rag import router as rag_router
from app.db.database import Base, engine
from app.models import Document, User


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Document Search Platform",
    description=(
        "Backend API for AI-powered document search "
        "using FastAPI, PostgreSQL, Qdrant and "
        "Hugging Face"
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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