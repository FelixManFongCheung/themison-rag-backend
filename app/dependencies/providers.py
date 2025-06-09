from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.embeddings import EmbeddingProvider, SentenceTransformerProvider
from app.core.storage import StorageProvider, PostgresVectorStore
from .db import get_db
from functools import lru_cache

@lru_cache()
def get_embedding_provider() -> EmbeddingProvider:
    """Get cached embedding provider instance"""
    return SentenceTransformerProvider()

def get_storage_provider(
    db: AsyncSession = Depends(get_db)
) -> StorageProvider:
    """Get vector storage provider instance"""
    return PostgresVectorStore(db) 