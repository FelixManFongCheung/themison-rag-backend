import os 
from sentence_transformers import SentenceTransformer
from typing import List
import uuid
from .lib.supabase_client import supabase_client
import asyncio

supabase = supabase_client()

# Function to insert documents with embeddings
async def insert_document(document):
    print(f"Processing {len(document)} documents", document)
    total_chunks = 0
    
    # Get embeddings and chunks from the document container
    embeddings = document['embeddings']
    chunks = document['chunks']
    print(len(chunks), len(embeddings))
    
    # Make sure we have the same number of embeddings as chunks
    if len(embeddings) != len(chunks):
        print(f"Warning: Number of embeddings ({len(embeddings)}) doesn't match number of chunks ({len(chunks)})")
        return
    
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
            await asyncio.to_thread(
                lambda: supabase.table("documents").insert({
                    "content": chunk.page_content,
                    "embedding": embedding_list,
                    "metadata": metadata
                }).execute()
            )
            
            total_chunks += 1
            
        except Exception as e:
            print(f"Error inserting chunk {i}: {str(e)}")

    print(f"Successfully inserted {total_chunks} chunks into the database")
    return total_chunks