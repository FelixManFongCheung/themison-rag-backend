import os
from pathlib import Path
from app.documents_processing.chunking import chunk
from app.documents_processing.embeddings import encode
from app.documents_processing.preprocessing import preprocessing
from langchain.schema import Document

def encode_doc(documents, chunk_size=1000, chunk_overlap=300):
    documents = [Document(page_content=preprocessing(doc.page_content), metadata=doc.metadata) 
                 for doc in documents]
    
    chunked_texts = chunk(chunk_size, chunk_overlap, documents)    
    # Extract just the text content from the Document objects before encoding
    text_strings = [doc.page_content for doc in chunked_texts]
    encoded_texts = encode(text_strings)
    return {"embeddings": encoded_texts, "chunks": chunked_texts}