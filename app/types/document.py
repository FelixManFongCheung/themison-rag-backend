from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

class Document(BaseModel):
    id: UUID
    name: str
    content: str
    metadata: Dict[str, Any]
    chunks: List[str]
    embedding: List[float]
    vector_store: str
    vector_id: str
    vector_index: int
    vector_score: float
    vector_metadata: Dict[str, Any]
    vector_chunks: List[str]
    vector_embedding: List[float]
    created_at: datetime
    updated_at: datetime