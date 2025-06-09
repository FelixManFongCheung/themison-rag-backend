from .base import IBaseService
from typing import List
from uuid import UUID
from app.contracts.document import DocumentCreate, DocumentUpdate, DocumentResponse

class IDocumentService(IBaseService[DocumentCreate, DocumentUpdate, DocumentResponse]):
    async def search(self, query: str) -> List[DocumentResponse]:
        """Search documents by content"""
        pass
    
    async def create(self, doc: DocumentCreate) -> DocumentResponse:
        """Create document"""
        pass
    
    async def get(self, doc_id: UUID) -> DocumentResponse:
        """Get document"""
        pass
    
    async def create_embedding(self, doc_id: UUID) -> DocumentResponse:
        """Generate and store embedding for document"""
        pass
    
    async def search_by_vector(self, query_vector: List[float], limit: int = 5) -> List[DocumentResponse]:
        """Search documents by vector similarity"""
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