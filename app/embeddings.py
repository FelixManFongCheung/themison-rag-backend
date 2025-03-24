import os
from functools import lru_cache
import time
from sentence_transformers import SentenceTransformer
import numpy as np

@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the embedding model from cache if available"""
    start_time = time.time()
    print("Loading embedding model...")
    
    # Check if we have a cached model
    if os.path.exists("model_cache/embedding_model"):
        model = SentenceTransformer("model_cache/embedding_model", trust_remote_code=True)
        print(f"Model loaded from cache in {time.time() - start_time:.2f} seconds")
    else:
        # Fallback to loading from the original source
        model = SentenceTransformer("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)
        print(f"Model loaded from source in {time.time() - start_time:.2f} seconds")
    
    return model

def encode(texts, batch_size=32):
    """Generate embeddings for the given texts with batching"""
    if not texts:
        return []
        
    model = get_embedding_model()
    
    # For small batches, encode directly
    if len(texts) <= batch_size:
        return model.encode(texts, convert_to_numpy=True)
    
    # For larger sets, process in batches
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = model.encode(
            batch,
            show_progress_bar=len(batch) > 100,
            convert_to_numpy=True
        )
        all_embeddings.append(batch_embeddings)
    
    # Combine all batches
    return np.vstack(all_embeddings)