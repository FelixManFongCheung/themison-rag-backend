from ..interfaces.document_service import IDocumentService
from app.contracts.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.models.documents import Document
from app.models.embedding import Embedding
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.core.embeddings import EmbeddingProvider
from app.core.storage import StorageProvider
from .utils.chunking import chunk_documents
from .utils.encoding import encode_texts
from .utils.preprocessing import preprocess_text
from langchain.schema import Document as LangchainDocument

class DocumentService(IDocumentService):
    def __init__(
        self, 
        db: AsyncSession,
        embedding_provider: EmbeddingProvider,
        storage_provider: StorageProvider
    ):
        self.db = db
        self.embedding_provider = embedding_provider
        self.storage_provider = storage_provider
        
    async def create_embedding(self, doc_id: UUID) -> DocumentResponse:
        # Get document
        result = await self.db.execute(select(Document).filter(Document.id == doc_id))
        if doc := result.scalar_one_or_none():
            # Generate embedding
            embedding_vector = await self.embedding_provider.get_embedding(doc.content)
            
            # Create or update embedding
            db_embedding = Embedding(
                document_id=doc.id,
                embedding=embedding_vector
            )
            self.db.add(db_embedding)
            await self.db.commit()
            
            return DocumentResponse.model_validate(doc)
        raise ValueError(f"Document {doc_id} not found")

    async def chunk(self, doc_id: UUID) -> List[DocumentResponse]:
        """Chunk document into smaller pieces"""
        result = await self.db.execute(select(Document).filter(Document.id == doc_id))
        if doc := result.scalar_one_or_none():
            # Convert to LangChain document format
            langchain_doc = LangchainDocument(
                page_content=doc.content,
                metadata=doc.metadata or {}
            )
            
            # Chunk the document
            chunked_docs = chunk_documents([langchain_doc])
            
            # Store chunks in document
            doc.chunks = {
                "chunks": [
                    {"content": d.page_content, "metadata": d.metadata}
                    for d in chunked_docs
                ]
            }
            await self.db.commit()
            
            return [DocumentResponse.model_validate(doc)]
        raise ValueError(f"Document {doc_id} not found")

    async def encode(self, doc_id: UUID) -> List[DocumentResponse]:
        """Encode document chunks"""
        result = await self.db.execute(select(Document).filter(Document.id == doc_id))
        if doc := result.scalar_one_or_none():
            if not doc.chunks:
                # If no chunks exist, create them first
                await self.chunk(doc_id)
                # Refresh doc to get chunks
                await self.db.refresh(doc)
            
            # Get chunks
            chunks = [
                LangchainDocument(
                    page_content=chunk["content"],
                    metadata=chunk["metadata"]
                )
                for chunk in doc.chunks["chunks"]
            ]
            
            # Generate embeddings
            embeddings = await encode_texts([c.page_content for c in chunks])
            
            # Store embeddings with chunks
            doc.chunks = {
                "chunks": [
                    {
                        "content": chunk["content"],
                        "metadata": chunk["metadata"],
                        "embedding": emb.tolist()
                    }
                    for chunk, emb in zip(doc.chunks["chunks"], embeddings)
                ]
            }
            await self.db.commit()
            
            return [DocumentResponse.model_validate(doc)]
        raise ValueError(f"Document {doc_id} not found")

    async def preprocess(self, doc_id: UUID) -> List[DocumentResponse]:
        """Preprocess document before chunking/encoding"""
        result = await self.db.execute(select(Document).filter(Document.id == doc_id))
        if doc := result.scalar_one_or_none():
            # Preprocess the content
            doc.content = preprocess_text(doc.content)
            await self.db.commit()
            
            return [DocumentResponse.model_validate(doc)]
        raise ValueError(f"Document {doc_id} not found") 