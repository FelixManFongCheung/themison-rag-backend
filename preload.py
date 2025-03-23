# preload.py
import os
import time
from sentence_transformers import SentenceTransformer

print("Preloading embedding model...")
start_time = time.time()

# Load the model
model = SentenceTransformer("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)


# Save the model to disk to ensure it's cached
os.makedirs("model_cache", exist_ok=True)
model.save("model_cache/embedding_model")

print(f"Model preloaded in {time.time() - start_time:.2f} seconds")