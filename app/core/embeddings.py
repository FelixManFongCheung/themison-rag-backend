from abc import ABC, abstractmethod
from typing import List
from sentence_transformers import SentenceTransformer
from app.core.config import get_settings

class EmbeddingProvider(ABC):
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        pass

class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self):
        settings = get_settings()
        self.model = SentenceTransformer(settings.embedding_model)
    
    async def get_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text)
        return embedding.tolist() 