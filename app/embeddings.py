import os
from functools import lru_cache
import time
from sentence_transformers import SentenceTransformer

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

def encode(texts):
    """Generate embeddings for the given texts"""
    model = get_embedding_model()
    return model.encode(texts)