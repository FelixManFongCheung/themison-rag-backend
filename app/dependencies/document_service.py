from ..services.interfaces.document_service import IDocumentService
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.models.documents import Document
from app.models.embedding import Embedding
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

class DocumentService(IDocumentService):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, schema: DocumentCreate) -> DocumentResponse:
        db_doc = Document(**schema.model_dump())
        self.db.add(db_doc)
        await self.db.commit()
        await self.db.refresh(db_doc)
        return DocumentResponse.model_validate(db_doc)
    
    async def get(self, id: UUID) -> DocumentResponse:
        result = await self.db.execute(select(Document).filter(Document.id == id))
        if doc := result.scalar_one_or_none():
            return DocumentResponse.model_validate(doc)
        raise ValueError(f"Document {id} not found")
    
    async def update(self, id: UUID, schema: DocumentUpdate) -> DocumentResponse:
        result = await self.db.execute(select(Document).filter(Document.id == id))
        if doc := result.scalar_one_or_none():
            for key, value in schema.model_dump(exclude_unset=True).items():
                setattr(doc, key, value)
            await self.db.commit()
            await self.db.refresh(doc)
            return DocumentResponse.model_validate(doc)
        raise ValueError(f"Document {id} not found")
    
    async def delete(self, id: UUID) -> None:
        result = await self.db.execute(select(Document).filter(Document.id == id))
        if doc := result.scalar_one_or_none():
            await self.db.delete(doc)
            await self.db.commit()
        else:
            raise ValueError(f"Document {id} not found")
    
    async def list(self) -> List[DocumentResponse]:
        result = await self.db.execute(select(Document))
        docs = result.scalars().all()
        return [DocumentResponse.model_validate(doc) for doc in docs]
    
    async def search(self, query: str) -> List[DocumentResponse]:
        # Implement full-text search logic
        result = await self.db.execute(
            select(Document).filter(Document.content.ilike(f"%{query}%"))
        )
        docs = result.scalars().all()
        return [DocumentResponse.model_validate(doc) for doc in docs]
    
    async def create_embedding(self, doc_id: UUID) -> DocumentResponse:
        # Implement embedding creation logic
        pass
    
    async def search_by_vector(self, query_vector: List[float], limit: int = 5) -> List[DocumentResponse]:
        # Implement vector similarity search
        pass 