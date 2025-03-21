import os 
import vecs
from sentence_transformers import SentenceTransformer
from typing import List
import uuid

password = os.getenv("SUPABASE_DB_PASSWORD")

DB_CONNECTION = f"postgresql://postgres:{password}@db.mkkxzqbwvksijsjecvhc.supabase.co:5432/postgres"

# create vector store client
vx = vecs.create_client(DB_CONNECTION)

docs = vx.get_collection(name="documents", dimension=1024)

class Document:
    def __init__(self, id: str, content: str, embedding: List[float], metadata: dict):
        self.id = id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata
        