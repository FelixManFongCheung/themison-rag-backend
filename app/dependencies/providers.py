from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.embeddings import EmbeddingProvider, SentenceTransformerProvider
from app.core.storage import StorageProvider, PostgresVectorStore
from .db import get_db

def get_embedding_provider() -> EmbeddingProvider:
    """Get embedding provider instance from app state (loaded at startup)"""
    from app.main import app_state
    if "embedding_provider" not in app_state:
        # Fallback to lazy loading if not in app state (e.g., during testing)
        return SentenceTransformerProvider()
    return app_state["embedding_provider"]

def get_storage_provider(
    db: AsyncSession = Depends(get_db)
) -> StorageProvider:
    """Get vector storage provider instance"""
    return PostgresVectorStore(db) 