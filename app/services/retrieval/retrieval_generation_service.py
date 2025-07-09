from typing import Any, AsyncGenerator, Dict, List

from app.core.embeddings import EmbeddingProvider

from .retriever import create_retriever, preprocess_query
from .utils.generation import call_llm_stream, generate_response


class RetrievalGenerationService:
    def __init__(self, embedding_provider: EmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.retriever = create_retriever(embedding_provider)
        
    async def process_query(self, query: str) -> AsyncGenerator[str, None]:
        """Process a query through the RAG pipeline"""
        # Preprocess the query
        processed_query = preprocess_query(query)
        
        # Retrieve relevant documents
        retrieved_docs = await self.retriever(processed_query)
        
        # Generate prompt
        prompt = generate_response(processed_query, retrieved_docs)
        
        # Get streaming response
        return await call_llm_stream(prompt)
        
    async def retrieve_documents(self, query: str, limit: int = 5) -> List[Dict[Any, Any]]:
        """Just retrieve documents without generation"""
        processed_query = preprocess_query(query)
        return await self.retriever(processed_query, override_match_count=limit) 