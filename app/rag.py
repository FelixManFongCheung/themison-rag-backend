from typing import List, Dict
from openai import OpenAI
from .database import SupabaseStore
from .indexing_processing.embeddings import EmbeddingModel
from .config import get_settings

class RAGSystem:
    def __init__(self):
        settings = get_settings()
        self.store = SupabaseStore()
        self.embedding_model = EmbeddingModel()
        self.llm_client = OpenAI(api_key=settings.openai_api_key)

    async def add_documents(self, texts: List[str], metadata: List[Dict] = None):
        """Add documents to the vector store"""
        if metadata is None:
            metadata = [{}] * len(texts)
        
        embeddings = self.embedding_model.get_embeddings(texts)
        
        for text, embedding, meta in zip(texts, embeddings, metadata):
            await self.store.add_document(text, embedding, meta)

    async def query(self, query: str, max_tokens: int = 1000) -> Dict:
        """Process a query through the RAG pipeline"""
        # Get query embedding
        query_embedding = self.embedding_model.get_embeddings(query)
        
        # Retrieve relevant documents
        results = await self.store.hybrid_search(query, query_embedding)
        
        # Prepare context
        context = "\n".join([f"Document {i+1}: {doc['content']}" 
                           for i, doc in enumerate(results)])
        
        # Generate response
        response = self.llm_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer based on the provided context."},
                {"role": "user", "content": f"""Context: {context}

                Question: {query}

                Please provide a detailed answer based on the context above. If the context doesn't contain enough information, say so."""}
            ],
            max_tokens=max_tokens
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": results
        }