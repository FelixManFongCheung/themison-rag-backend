from typing import List, Dict, Any, AsyncGenerator
from .utils.retrieval_generation.generation import generate_response, call_llm_stream
from .utils.retrieval_generation.retriever import create_retriever, preprocess_query
from app.core.embeddings import EmbeddingProvider

class RetrievalGenerationService:
    def __init__(self, embedding_provider: EmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.retriever = create_retriever()
        
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