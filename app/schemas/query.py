from .base import BaseSchema, TimestampedSchema
from uuid import UUID
from datetime import datetime

class QueryBase(BaseSchema):
    query: str

class QueryCreate(QueryBase):
    pass

class QueryResponse(QueryBase, TimestampedSchema):
    id: UUID 