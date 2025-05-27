from supabase import create_client
from typing import List, Dict, Optional
import numpy as np
from .config import get_settings

class SupabaseStore:
    def __init__(self):
        settings = get_settings()
        self.client = create_client(settings.supabase_url, settings.supabase_service_key)
        
    async def get_document(self, document_id: str):
        """Get a document from the vector store"""
        return self.client.table('documents').select('*').eq('id', document_id).execute()

    async def add_document(self, content: str, embedding: List[float], metadata: Optional[Dict] = None):
        """Add a document to the vector store"""
        data = {
            'content': content,
            'embedding': embedding,
            'metadata': metadata or {}
        }
        return self.client.table('documents').insert(data).execute()

    async def hybrid_search(self, 
                          query_text: str, 
                          query_embedding: List[float],
                          limit: int = 3) -> List[Dict]:
        """Perform hybrid search"""
        response = self.client.rpc(
            'hybrid_search_documents',
            {
                'query_text': query_text,
                'query_embedding': query_embedding,
                'match_count': limit,
                'text_search_weight': 0.3,
                'vector_search_weight': 0.7
            }
        ).execute()
        
        return response.data