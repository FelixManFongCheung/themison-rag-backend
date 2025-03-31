from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk(chunk_size, chunk_overlap, documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],  # Try to split at paragraph boundaries first
        keep_separator=True  # Keep the separators to preserve exact text
    )
    texts = text_splitter.split_documents(documents)
    return texts