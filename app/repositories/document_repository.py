from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:

    def create(
        self,
        db: Session,
        filename: str,
        filepath: str,
        user_id: int,
    ) -> Document:

        document = Document(
            filename=filename,
            filepath=filepath,
            user_id=user_id,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    def get_all_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[Document]:

        return (
            db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.id.desc())
            .all()
        )

    def get_by_id_and_user(
        self,
        db: Session,
        document_id: int,
        user_id: int,
    ):

        return (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id,
            )
            .first()
        )

    def delete(
        self,
        db: Session,
        document: Document,
    ) -> None:

        db.delete(document)
        db.commit()