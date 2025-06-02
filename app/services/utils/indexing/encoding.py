import os
from pathlib import Path
from app.services.indexing.chunking import chunk
from app.services.indexing.embeddings import encode
from app.services.indexing.preprocessing import preprocessing
from langchain.schema import Document
import concurrent.futures

def encode_doc(documents, chunk_size=1000, chunk_overlap=300, batch_size=32):
    # Preprocess documents in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        preprocessed_docs = list(executor.map(
            lambda doc: Document(page_content=preprocessing(doc.page_content), metadata=doc.metadata),
            documents
        ))
    
    # Chunk the documents
    chunked_texts = chunk(chunk_size, chunk_overlap, preprocessed_docs)
    
    # Extract text content
    text_strings = [doc.page_content for doc in chunked_texts]
    
    # Process in batches
    all_embeddings = []
    for i in range(0, len(text_strings), batch_size):
        batch = text_strings[i:i+batch_size]
        batch_embeddings = encode(batch)
        all_embeddings.extend(batch_embeddings)
    
    return {"embeddings": all_embeddings, "chunks": chunked_texts}