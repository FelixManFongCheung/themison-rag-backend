from sqlalchemy import Column, JSON, DateTime, ForeignKey, Vector
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from datetime import datetime, UTC
import uuid
from .documents import Document
from typing import List

class Embedding(Base):
    __tablename__ = 'embeddings'
    
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[UUID] = Column(UUID(as_uuid=True), ForeignKey('documents.id'), unique=True)
    embedding: Mapped[List[float]] = Column(Vector(1024))
    created_at: Mapped[DateTime] = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[DateTime] = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    document: Mapped[Document] = relationship("Document", back_populates="embeddings", single_parent=True)