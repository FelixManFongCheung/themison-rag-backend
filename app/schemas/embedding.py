from .base import BaseSchema, TimestampedSchema
from uuid import UUID
from typing import List

class EmbeddingBase(BaseSchema):
    embedding: List[float]

class EmbeddingCreate(EmbeddingBase):
    document_id: UUID

class EmbeddingResponse(EmbeddingBase, TimestampedSchema):
    id: UUID
    document_id: UUID 