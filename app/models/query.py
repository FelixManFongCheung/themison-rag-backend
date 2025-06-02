from .base import Base
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime, UTC
import uuid
from uuid import UUID

class Query(Base):
    __tablename__ = 'queries'
    
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query: Mapped[str] = Column(String)
    created_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(UTC))