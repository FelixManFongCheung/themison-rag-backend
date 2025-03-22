from app.documents_processing.embeddings import encode
from app.lib.supabase_client import supabase_client
from typing import List, Dict, Any, Optional

supabase = supabase_client()

def preprocess_query(query: str) -> str:
    """Clean and normalize the query text."""
    return query.strip()

def create_embeddings(query: str):
    """Create embeddings for the query."""
    preprocessed_query = preprocess_query(query)
    embeddings = encode(preprocessed_query)
    return embeddings

def create_retriever(
    match_count: int = 10, 
    match_threshold: float = 0.0,
    alpha: float = 0.5  # Balance between vector and keyword search
):
    """
    Create a hybrid retriever that combines vector similarity and keyword search.
    
    Args:
        match_count: Maximum number of results to return
        match_threshold: Minimum similarity threshold
        alpha: Balance between vector and text search (0=keywords only, 1=vectors only)
    
    Returns:
        A retrieval function that takes a query string and returns matching documents
    """
    
    def retrieve(
        query: str, 
        override_alpha: Optional[float] = None,
        override_threshold: Optional[float] = None,
        override_count: Optional[int] = None
    ) -> List[Dict[Any, Any]]:
        # Generate embedding for the query
        query_embedding = create_embeddings(query)
        
        # Use override parameters if provided, otherwise use defaults
        a = override_alpha if override_alpha is not None else alpha
        threshold = override_threshold if override_threshold is not None else match_threshold
        count = override_count if override_count is not None else match_count
        
        # Perform hybrid search in Supabase
        result = supabase.rpc(
            "hybrid_search",
            {
                "query_text": query,
                "query_embedding": query_embedding,
                "alpha": a,
                "match_threshold": threshold,
                "match_count": count
            }
        ).execute()
        
        if len(result.data) == 0:
            return []
            
        return result.data
        
    return retrieve