from .base import BaseSchema, TimestampedSchema
from uuid import UUID
from typing import Optional, Dict, List
from datetime import datetime

class DocumentBase(BaseSchema):
    content: str
    metadata: Optional[Dict] = None
    chunks: Optional[Dict] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseSchema):
    content: Optional[str] = None
    metadata: Optional[Dict] = None
    chunks: Optional[Dict] = None

class DocumentResponse(DocumentBase, TimestampedSchema):
    id: UUID
    embedding_id: Optional[UUID] = None