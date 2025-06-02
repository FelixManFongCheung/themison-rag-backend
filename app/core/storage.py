from abc import ABC, abstractmethod
from typing import List
from app.models.documents import Document
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

class StorageProvider(ABC):
    @abstractmethod
    async def similarity_search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[Document]:
        pass

class PostgresVectorStore(StorageProvider):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def similarity_search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[Document]:
        # Using PostgreSQL's vector similarity search
        # This is a simplified example - you might want to use pgvector
        query = select(Document).join(Document.embedding).order_by(
            Document.embedding.cosine_distance(query_vector)
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all() 