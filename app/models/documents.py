from sqlalchemy import Column, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
from .base import Base  
from sqlalchemy.orm import relationship, Mapped
import uuid
from .embedding import Embedding
from .chat_sessions import ChatSession
from typing import List

class Document(Base):
    __tablename__ = 'documents'
    
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metadata: Mapped[JSON] = Column(JSON)
    chunks: Mapped[JSON] = Column(JSON)
    content: Mapped[Text] = Column(Text)
    embedding: Mapped[Embedding] = relationship("Embedding", back_populates="document", uselist=False, cascade="all, delete-orphan")
    created_at: Mapped[DateTime] = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[DateTime] = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    chat_sessions: Mapped[List[ChatSession]] = relationship("ChatSession", secondary="chat_document_links", back_populates="documents")
    
