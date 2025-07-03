from .base import IBaseService
from typing import List
from uuid import UUID
from app.contracts.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.models.chunks import DocumentChunk

class IDocumentService(IBaseService[DocumentCreate, DocumentUpdate, DocumentResponse]):
    async def create_embedding(self, doc_id: UUID) -> DocumentResponse:
        """Generate and store embedding for document"""
        pass
    
    async def chunk(self, doc_id: UUID) -> List[DocumentResponse]:
        """Chunk document"""
        pass
    
    async def encode(self, doc_id: UUID) -> List[DocumentResponse]:
        """Encode document"""
        pass
    
    async def preprocess(self, doc_id: UUID) -> List[DocumentResponse]:
        """Preprocess document"""
        pass
    
    async def insert_single_chunk(
        self,
        document_chunk: DocumentChunk
    ) -> List[DocumentResponse]:
        """Insert a single chunk"""
        pass