from sqlalchemy import Column, JSON, DateTime, ForeignKey, Vector
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from datetime import datetime, UTC
import uuid
from .documents import Document
from typing import List, Dict, Integer, Text


# New table for individual chunks
class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[UUID] = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    content: Mapped[str] = Column(Text, nullable=False)
    chunk_index: Mapped[int] = Column(Integer, nullable=False)
    metadata: Mapped[Dict] = Column(JSON)
    embedding: Mapped[List[float]] = Column(Vector(1024))
    created_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
