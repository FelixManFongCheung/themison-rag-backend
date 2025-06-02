from .base import BaseSchema, TimestampedSchema
from pydantic import EmailStr, Field
from typing import Optional
from uuid import UUID

class UserBase(BaseSchema):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(min_length=8, description="User password, minimum 8 characters")

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase, TimestampedSchema):
    id: UUID
    # Note: password is intentionally excluded from response
