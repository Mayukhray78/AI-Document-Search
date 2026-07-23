import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.ai.embeddings import EmbeddingModel
from app.ai.pdf_reader import PDFReader
from app.ai.text_splitter import TextSplitter
from app.ai.vector_store import VectorStore
from app.repositories.document_repository import DocumentRepository


repo = DocumentRepository()

reader = PDFReader()
splitter = TextSplitter()
embedding_model = EmbeddingModel()
vector_store = VectorStore()

UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024


class DocumentService:

    def upload(
        self,
        db: Session,
        file: UploadFile,
        user_id: int,
    ):

        original_filename = Path(
            file.filename or ""
        ).name

        if not original_filename:
            raise Exception("A filename is required")

        if Path(original_filename).suffix.lower() != ".pdf":
            raise Exception("Only PDF files are allowed")

        if file.content_type != "application/pdf":
            raise Exception("Invalid PDF content type")

        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size == 0:
            raise Exception("The uploaded PDF is empty")

        if file_size > MAX_FILE_SIZE:
            raise Exception(
                "The PDF cannot be larger than 10 MB"
            )

        os.makedirs(
            UPLOAD_FOLDER,
            exist_ok=True,
        )

        stored_filename = (
            f"{uuid4().hex}_{original_filename}"
        )

        filepath = os.path.join(
            UPLOAD_FOLDER,
            stored_filename,
        )

        try:
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(
                    file.file,
                    buffer,
                )

            extracted_text = reader.extract_text(
                filepath
            )

            if not extracted_text.strip():
                raise Exception(
                    "No readable text was found in the PDF"
                )

            chunks = splitter.split_text(
                extracted_text
            )

            if not chunks:
                raise Exception(
                    "The PDF could not be divided into text chunks"
                )

            embeddings = (
                embedding_model.generate_embeddings(
                    chunks
                )
            )

            document = repo.create(
                db=db,
                filename=original_filename,
                filepath=filepath,
                user_id=user_id,
            )

            vector_store.store_embeddings(
                chunks=chunks,
                embeddings=embeddings,
                document_id=document.id,
                user_id=user_id,
            )

            print("\n" + "=" * 80)
            print("DOCUMENT INDEXED SUCCESSFULLY")
            print("=" * 80)
            print(f"Document ID : {document.id}")
            print(f"User ID     : {user_id}")
            print(f"Filename    : {original_filename}")
            print(f"Chunks      : {len(chunks)}")
            print("=" * 80)

            return document

        except Exception:
            if os.path.exists(filepath):
                os.remove(filepath)

            raise

    def get_all(
        self,
        db: Session,
        user_id: int,
    ):

        return repo.get_all_by_user(
            db=db,
            user_id=user_id,
        )

    def delete(
        self,
        db: Session,
        document_id: int,
        user_id: int,
    ) -> None:

        document = repo.get_by_id_and_user(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        if not document:
            raise Exception(
                "Document not found or access denied"
            )

        vector_store.delete_document(
            document_id=document.id,
            user_id=user_id,
        )

        if os.path.exists(document.filepath):
            os.remove(document.filepath)

        repo.delete(
            db=db,
            document=document,
        )

        print(
            f"Document {document_id} deleted successfully."
        )