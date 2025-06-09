from .base import BaseContract, TimestampedContract
from uuid import UUID
from typing import List

class EmbeddingBase(BaseContract):
    embedding: List[float]

class EmbeddingCreate(EmbeddingBase):
    document_id: UUID

class EmbeddingResponse(EmbeddingBase, TimestampedContract):
    id: UUID
    document_id: UUID 