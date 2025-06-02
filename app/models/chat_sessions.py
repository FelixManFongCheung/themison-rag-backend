from sqlalchemy import Column, Text, JSON, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
from .base import Base
from sqlalchemy.orm import relationship, Mapped
from typing import List
import uuid
from .chat_messages import ChatMessage
from .documents import Document

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = Column(UUID(as_uuid=True))
    title: Mapped[str] = Column(String(255))
    created_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationship to messages
    messages: Mapped[List[ChatMessage]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    # Many-to-many with documents
    documents: Mapped[List[Document]] = relationship(
        "Document",
        secondary="chat_document_links",
        back_populates="chat_sessions"
    )