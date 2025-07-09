import asyncio
import re
from typing import Any, Dict, List, Optional

import numpy as np

from app.core.embeddings import EmbeddingProvider
from app.supabase_client.supabase_client import supabase_client

supabase = supabase_client()

def preprocess_query(query: str) -> str:
    """Clean and normalize the query text."""
    return query.strip()

def preprocess_query_for_tsquery(query: str) -> str:
    """
    Preprocess a natural language query for PostgreSQL's ts_query.
    Converts spaces to & operators and handles special characters.
    """
    # Remove special characters that might cause syntax errors
    clean_query = re.sub(r'[!@#$%^&*()+=\[\]{};:"\\|,.<>/?]', ' ', query)
    
    # Split into words and filter out empty strings
    words = [word.strip() for word in clean_query.split() if word.strip()]
    
    # For very short queries or empty queries after cleaning
    if not words:
        return ""  # Return empty string
        
    # Join words with & operator for AND logic
    formatted_query = ' & '.join(words)
    
    return formatted_query

async def create_embeddings(query: str, embedding_provider: EmbeddingProvider):
    """Create embeddings for the query asynchronously."""
    preprocessed_query = preprocess_query(query)
    # Use the embedding provider to generate embeddings
    embeddings = embedding_provider.get_embedding([preprocessed_query])
    
    # Return the first (and only) embedding
    return embeddings[0] if embeddings else []

def create_retriever(
    embedding_provider: EmbeddingProvider,
    match_count: int = 10,
):  
    async def retrieve(
        query: str,
        override_match_count: Optional[int] = None
    ) -> List[Dict[Any, Any]]:
        # Generate embedding for the query
        query_embedding = await create_embeddings(query, embedding_provider)
        
        # Use override parameters if provided, otherwise use defaults
        count = override_match_count if override_match_count is not None else match_count        
        # Call the hybrid_search function using RPC
        result = await asyncio.to_thread(
            lambda: supabase.rpc(
                "hybrid_search",
                {
                    "query_text": query,
                    "query_embedding": query_embedding,
                    "match_count": count
                }
            ).execute()
        )
        
        # Ensure all data is JSON serializable
        return _ensure_serializable(result.data)
        
    return retrieve

def _ensure_serializable(data):
    """Recursively convert any NumPy arrays to lists to ensure JSON serializability."""
    if isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, dict):
        return {k: _ensure_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_ensure_serializable(item) for item in data]
    else:
        return data