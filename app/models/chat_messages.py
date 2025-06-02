from sqlalchemy import Column, Text, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id'))
    content = Column(Text)
    role = Column(String(50))  # "user" or "assistant"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Reference to specific document chunks used
    document_chunk_ids = Column(ARRAY(String))  # IDs of document chunks used
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")