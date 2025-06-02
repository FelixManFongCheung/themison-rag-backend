from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.document_service import DocumentService
from app.services.interfaces.document_service import IDocumentService
from app.core.embeddings import EmbeddingProvider, SentenceTransformerProvider
from app.core.storage import StorageProvider, PostgresVectorStore
from app.dependencies.database import get_db
from functools import lru_cache

@lru_cache()
def get_embedding_provider() -> EmbeddingProvider:
    return SentenceTransformerProvider()

def get_storage_provider(
    db: AsyncSession = Depends(get_db)
) -> StorageProvider:
    return PostgresVectorStore(db)

async def get_document_service(
    db: AsyncSession = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
    storage_provider: StorageProvider = Depends(get_storage_provider)
) -> IDocumentService:
    return DocumentService(
        db=db,
        embedding_provider=embedding_provider,
        storage_provider=storage_provider
    ) 