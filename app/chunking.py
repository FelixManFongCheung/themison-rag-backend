from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk(chunk_size, chunk_overlap, documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    texts = text_splitter.split_documents(documents)
    return texts