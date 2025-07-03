from abc import ABC, abstractmethod
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import get_settings
import asyncio
import numpy as np

class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    async def get_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        pass

class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self):
        settings = get_settings()
        self.model = SentenceTransformer(settings.embedding_model)
    
    def get_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    async def get_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for multiple texts with batching"""
        if not texts:
            return []
        
        async def process_batch(batch: List[str]) -> np.ndarray:
            return await asyncio.to_thread(
                lambda: self.model.encode(
                    batch,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
            )
        
        if len(texts) <= batch_size:
            embeddings = await process_batch(texts)
            return [emb.tolist() for emb in embeddings]
        
        # Process in batches
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        batch_embeddings = await asyncio.gather(*[process_batch(batch) for batch in batches])
        
        # Combine all batches and convert to lists
        all_embeddings = np.vstack(batch_embeddings)
        return [emb.tolist() for emb in all_embeddings]

# different embedding models comparison in the future hence the factory design 