import os
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import asyncio

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model from cache if available"""
    model_path = "model_cache/embedding_model"
    model_name = "Alibaba-NLP/gte-large-en-v1.5"
    
    return (
        SentenceTransformer(model_path, trust_remote_code=True)
        if os.path.exists(model_path)
        else SentenceTransformer(model_name, trust_remote_code=True)
    )

async def encode_texts(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """Generate embeddings for the given texts with batching"""
    if not texts:
        return np.array([])
    
    model = get_embedding_model()
    
    async def process_batch(batch: List[str]) -> np.ndarray:
        return await asyncio.to_thread(
            lambda: model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True
            )
        )
    
    if len(texts) <= batch_size:
        return await process_batch(texts)
    
    # Process in batches
    batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
    embeddings = await asyncio.gather(*[process_batch(batch) for batch in batches])
    
    return np.vstack(embeddings)