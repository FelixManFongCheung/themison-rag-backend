from .base import BaseContract, TimestampedContract
from uuid import UUID
from typing import Optional, Dict

class DocumentBase(BaseContract):
    content: str
    metadata: Optional[Dict] = None
    chunks: Optional[Dict] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseContract):
    content: Optional[str] = None
    metadata: Optional[Dict] = None
    chunks: Optional[Dict] = None

class DocumentResponse(DocumentBase, TimestampedContract):
    id: UUID
    embedding_id: Optional[UUID] = None
    
class DocumentUpload(BaseContract):
    document_url: str
