import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from app.documents_processing.chunking import chunk
from app.documents_processing.embeddings import encode
from app.documents_processing.preprocessing import preprocessing
from langchain.schema import Document

def encode_doc(path, chunk_size=1000, chunk_overlap=300):
    loader = PyPDFLoader(path)
    documents = loader.load()
    
    documents = [Document(page_content=preprocessing(doc.page_content), metadata=doc.metadata) 
                 for doc in documents]
    
    chunked_texts = chunk(chunk_size, chunk_overlap, documents)    
    # Extract just the text content from the Document objects before encoding
    text_strings = [doc.page_content for doc in chunked_texts]
    encoded_texts = encode(text_strings)
    return {"embeddings": encoded_texts, "chunks": chunked_texts}

# def batch_encode_directory(directory_path):
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
# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(project_root, "data", "Intership agreement and NDA Felix Fong Cheung Man- March 2025 (1).pdf")
encoded_documents = [encode_doc(pdf_path)]
