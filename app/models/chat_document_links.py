from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from datetime import datetime, UTC

class ChatDocumentLink(Base):
    __tablename__ = 'chat_document_links'
    
    chat_session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id'), primary_key=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    
    usage_count = Column(Integer, default=1)
    first_used_at = Column(DateTime, default=lambda: datetime.now(UTC))
    last_used_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))