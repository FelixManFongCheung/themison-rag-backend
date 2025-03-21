import os 
from sentence_transformers import SentenceTransformer
from typing import List
import uuid
from .encoding import encoded_documents
from .lib.supabase_client import supabase_client

supabase = supabase_client()

class Document:
    def __init__(self, id: str, content: str, embedding: List[float], metadata: dict):
        self.id = id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata

# Function to insert documents with embeddings
def insert_documents(documents):
    print(f"Processing {len(documents)} documents")
    total_chunks = 0
    
    for doc_container in documents:
        # Get embeddings and chunks from the document container
        embeddings = doc_container['embeddings']
        chunks = doc_container['chunks']
        print(len(chunks), len(embeddings))
        
        # Make sure we have the same number of embeddings as chunks
        if len(embeddings) != len(chunks):
            print(f"Warning: Number of embeddings ({len(embeddings)}) doesn't match number of chunks ({len(chunks)})")
            continue
        
        # Insert each chunk with its corresponding embedding
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            try:
                # Convert NumPy array to Python list for JSON serialization
                embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
                
                # Extract metadata from the chunk
                metadata = chunk.metadata.copy() if hasattr(chunk, 'metadata') else {}
                
                # Add additional metadata if needed
                metadata['chunk_index'] = i
                
                # Insert into Supabase
                supabase.table("documents").insert({
                    "id": str(uuid.uuid4()),
                    "content": chunk.page_content,
                    "embedding": embedding_list,
                    "metadata": metadata
                }).execute()
                
                total_chunks += 1
                
            except Exception as e:
                print(f"Error inserting chunk {i}: {str(e)}")
    
    print(f"Successfully inserted {total_chunks} chunks into the database")
    return total_chunks

# Function to search for similar documents
def search_similar_documents(query_embedding, match_count=5):
    # Use RPC call to a stored procedure for vector search
    result = supabase.rpc(
        'match_documents',
        {'query_embedding': query_embedding, 'match_count': match_count}
    ).execute()
    
    return result.data

# Execute the insert_documents function with the encoded documents
insert_documents(encoded_documents)