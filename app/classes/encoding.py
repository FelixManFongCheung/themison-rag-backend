import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from ..services.indexing.chunking import chunk
from ..services.indexing.embeddings import encode

def encode_doc(path, chunk_size=250, chunk_overlap=25):
    loader = PyPDFLoader(path)
    documents = loader.load()
    texts = chunk(chunk_size, chunk_overlap, documents)
    print(texts)
    # return encode(texts)

def batch_encode_directory(directory_path):
    """
    Encode all PDF files in the specified directory
    """
    directory = Path(directory_path)
    encoded_docs = {}
    
    for file_path in directory.glob("*.pdf"):
        print(f"Processing: {file_path}")
        try:
            encoded_docs[file_path.name] = encode_doc(str(file_path))
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    return encoded_docs

# Example usage:
if __name__ == "__main__":
    encoded_documents = batch_encode_directory("../data/")
    