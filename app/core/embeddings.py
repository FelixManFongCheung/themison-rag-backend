from abc import ABC, abstractmethod
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import get_settings

class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass

class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self):
        settings = get_settings()
        self.model = SentenceTransformer(settings.embedding_model)
    
    def get_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text)
        return embedding.tolist() 

# different embedding models comparison in the future hence the factory design 