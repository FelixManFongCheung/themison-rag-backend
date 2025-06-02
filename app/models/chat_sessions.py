from sqlalchemy import Column, Text, JSON, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
from .base import Base
from sqlalchemy.orm import relationship
import uuid

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    title = Column(String(255))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    # Many-to-many with documents
    documents = relationship(
        "Document",
        secondary="chat_document_links",
        back_populates="chat_sessions"
    )