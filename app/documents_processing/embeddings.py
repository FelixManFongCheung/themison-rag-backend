from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)

def encode(documents):
    embeddings = model.encode(documents)
    return embeddings
    