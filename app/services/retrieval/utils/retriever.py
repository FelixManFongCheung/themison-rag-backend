from ..indexing.embeddings import encode_texts
from app.lib.supabase_client import supabase_client
from typing import List, Dict, Any, Optional
import asyncio
import numpy as np
import re

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

async def create_embeddings(query: str):
    """Create embeddings for the query asynchronously."""
    preprocessed_query = preprocess_query(query)
    # Run potentially CPU-intensive encoding in a thread pool
    embeddings = await encode_texts([preprocessed_query])
    
    # Convert NumPy array to list if needed
    if isinstance(embeddings, np.ndarray):
        embeddings = embeddings.tolist()[0]  # Take first embedding since we only encoded one text
    
    return embeddings

def create_retriever(
    match_count: int = 10,
):  
    async def retrieve(
        query: str,
        override_match_count: Optional[int] = None
    ) -> List[Dict[Any, Any]]:
        # Generate embedding for the query
        query_embedding = await create_embeddings(query)
        
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