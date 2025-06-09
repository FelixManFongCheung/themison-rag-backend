from .base import BaseContract, TimestampedContract
from uuid import UUID

class QueryBase(BaseContract):
    query: str

class QueryCreate(QueryBase):
    pass

class QueryResponse(QueryBase, TimestampedContract):
    id: UUID 