from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    filepath = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")