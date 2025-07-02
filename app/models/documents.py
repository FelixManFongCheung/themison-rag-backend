from sqlalchemy import Column, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
from .base import Base  
from sqlalchemy.orm import relationship, Mapped
import uuid
from .chat_sessions import ChatSession
from typing import List, Integer, String

class Document(Base):
    __tablename__ = 'documents'
    
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = Column(UUID(as_uuid=True), nullable=False)  # Owner
    original_filename: Mapped[str] = Column(String(255), nullable=False)
    storage_url: Mapped[str] = Column(Text, nullable=False)
    file_size: Mapped[int] = Column(Integer)
    processing_status: Mapped[str] = Column(String(50), default="pending")
    metadata: Mapped[JSON] = Column(JSON)
    chunks: Mapped[JSON] = Column(JSON)
    content: Mapped[Text] = Column(Text)
    total_pages: Mapped[int] = Column(Integer)
    total_chunks: Mapped[int] = Column(Integer)
    created_at: Mapped[DateTime] = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[DateTime] = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    chat_sessions: Mapped[List[ChatSession]] = relationship("ChatSession", secondary="chat_document_links", back_populates="documents")
    
