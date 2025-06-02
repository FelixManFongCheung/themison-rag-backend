from .interfaces.document_service import IDocumentService
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.models.documents import Document
from app.models.embedding import Embedding
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.core.embeddings import EmbeddingProvider
from app.core.storage import StorageProvider
from .utils.indexing.chunking import chunk_documents
from .utils.indexing.embeddings import encode_texts
from .utils.indexing.preprocessing import preprocess_text
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
    
    async def create(self, schema: DocumentCreate) -> DocumentResponse:
        db_doc = Document(**schema.model_dump())
        self.db.add(db_doc)
        await self.db.commit()
        await self.db.refresh(db_doc)
        
        # Process document in background
        await self.preprocess(db_doc.id)
        await self.chunk(db_doc.id)
        await self.encode(db_doc.id)
        
        return DocumentResponse.model_validate(db_doc)
    
    async def get(self, id: UUID) -> DocumentResponse:
        result = await self.db.execute(select(Document).filter(Document.id == id))
        if doc := result.scalar_one_or_none():
            return DocumentResponse.model_validate(doc)
        raise ValueError(f"Document {id} not found")
    
    async def update(self, id: UUID, schema: DocumentUpdate) -> DocumentResponse:
        result = await self.db.execute(select(Document).filter(Document.id == id))
        if doc := result.scalar_one_or_none():
            for key, value in schema.model_dump(exclude_unset=True).items():
                setattr(doc, key, value)
            await self.db.commit()
            await self.db.refresh(doc)
            
            # Reprocess document if content changed
            if 'content' in schema.model_dump(exclude_unset=True):
                await self.preprocess(doc.id)
                await self.chunk(doc.id)
                await self.encode(doc.id)
                
            return DocumentResponse.model_validate(doc)
        raise ValueError(f"Document {id} not found")
    
    async def delete(self, id: UUID) -> None:
        result = await self.db.execute(select(Document).filter(Document.id == id))
        if doc := result.scalar_one_or_none():
            await self.db.delete(doc)
            await self.db.commit()
        else:
            raise ValueError(f"Document {id} not found")
    
    async def list(self) -> List[DocumentResponse]:
        result = await self.db.execute(select(Document))
        docs = result.scalars().all()
        return [DocumentResponse.model_validate(doc) for doc in docs]
    
    async def search(self, query: str) -> List[DocumentResponse]:
        # Get embedding for query
        query_embedding = await self.embedding_provider.get_embedding(query)
        
        # Search by vector similarity
        return await self.search_by_vector(query_embedding)
    
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
    
    async def search_by_vector(self, query_vector: List[float], limit: int = 5) -> List[DocumentResponse]:
        similar_docs = await self.storage_provider.similarity_search(
            query_vector,
            limit=limit
        )
        return [DocumentResponse.model_validate(doc) for doc in similar_docs]

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