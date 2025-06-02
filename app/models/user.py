from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Mapped
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from datetime import datetime, UTC
import uuid

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    role: Mapped[UserRole] = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))