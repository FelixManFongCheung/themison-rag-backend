from .base import IBaseService
from typing import List
from app.schemas.query import QueryCreate, QueryUpdate, QueryResponse
from app.schemas.document import DocumentResponse

class IQueryService(IBaseService[QueryCreate, QueryUpdate, QueryResponse]):
    async def search_documents(self, query: str) -> List[DocumentResponse]:
        """Search documents using the query"""
        pass
    
    async def create_embedding(self, query: str) -> List[float]:
        """Generate embedding for query"""
        pass

    async def search_by_vector(self, query_vector: List[float], limit: int = 5) -> List[DocumentResponse]:
        """Search documents by vector similarity"""
        pass