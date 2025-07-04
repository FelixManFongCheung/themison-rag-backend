# app/services/indexing/document_service.py
from ..interfaces.document_service import IDocumentService
from app.contracts.document import DocumentCreate, DocumentResponse
from app.models.documents import Document
from app.models.chunks import DocumentChunk
from app.core.embeddings import EmbeddingProvider
from app.core.storage import StorageProvider

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from fastapi import UploadFile
import pypdf as PyPDF2
import io
import requests

# Import your utils
from .utils.chunking import chunk_documents
from .utils.preprocessing import preprocess_text
from langchain.schema import Document as LangchainDocument

from app.db.session import engine
from app.models.base import Base
from datetime import datetime, UTC


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
    
    async def parse_pdf(self, document_url: str) -> str:
        """Extract text content from PDF file"""
        try:
            # Read PDF content
            response = requests.get(document_url)
            content = response.content
            pdf_file = io.BytesIO(content)
            
            # Extract text using PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            if not text_content.strip():
                raise ValueError("No text content found in PDF")
                
            return text_content
            
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    async def preprocess_content(self, content: str) -> str:
        """Preprocess text content"""
        return preprocess_text(content, clean_whitespace=True)
    
    async def chunk_content(
        self, 
        content: str, 
        metadata: Dict[str, Any] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[LangchainDocument]:
        """Split content into chunks"""
        
        doc = LangchainDocument(
            page_content=content,
            metadata=metadata or {}
        )
        
        chunks = chunk_documents([doc], chunk_size, chunk_overlap)
        return chunks
    
    async def generate_embeddings(self, chunks: List[LangchainDocument]) -> List[List[float]]:
        """Generate embeddings for chunks"""
        
        texts = [chunk.page_content for chunk in chunks]
        
        embeddings = self.embedding_provider.get_embeddings_batch(texts)
        
        return embeddings
    
    async def insert_document_with_chunks(
        self,
        title: str, 
        document_id: UUID,  # Existing document ID from frontend
        content: str,
        chunks: List[LangchainDocument],
        embeddings: List[List[float]],
        metadata: Dict[str, Any] = None,
        user_id: UUID = None
    ) -> DocumentResponse:
        """Process existing document and add chunks with embeddings"""
        
        await self.ensure_tables_exist()
        
        try:
            # Find existing document that frontend already created
            document = await self.db.get(Document, document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found. Frontend should create it first.")
            
            # Optionally update document with processed content
            if content:
                document.content = content
            if metadata:
                # Merge with existing metadata
                existing_metadata = document.metadata or {}
                document.metadata = {**existing_metadata, **metadata}
            
            # No need to add document - it already exists and SQLAlchemy is tracking it
            await self.db.flush()  # Save any document updates
            
            # Add chunks that reference the existing document
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_record = DocumentChunk(
                    id=uuid4(),
                    document_id=document.id,  # Reference existing document
                    content=chunk.page_content,
                    chunk_index=i,
                    metadata={**chunk.metadata, "chunk_index": i},
                    embedding=embedding,
                    created_at=datetime.now(UTC)
                )
                self.db.add(chunk_record)  # Add NEW chunk
            
            await self.db.commit()
            await self.db.refresh(document)
            
            return DocumentResponse.model_validate(document)
        
        except ValueError as e:
            await self.db.rollback()
            raise e  # Re-raise ValueError as-is
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            raise RuntimeError(f"Failed to process document chunks: {str(e)}")
    
    async def process_pdf_complete(
        self,
        document_url: str,
        document_id: UUID,  # Existing document ID from frontend
        user_id: UUID = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> DocumentResponse:
        """Complete PDF processing pipeline for existing document"""
        
        try:
            # Step 1: Parse PDF from URL
            content = await self.parse_pdf(document_url)
            document_filename = document_url.split("/")[-1]
            
            # Step 2: Preprocess content
            preprocessed_content = await self.preprocess_content(content)
            
            # Step 3: Chunk content
            metadata = {"filename": document_filename, "content_type": "application/pdf"}
            chunks = await self.chunk_content(
                preprocessed_content, 
                metadata, 
                chunk_size, 
                chunk_overlap
            )
            
            # Step 4: Generate embeddings
            embeddings = await self.generate_embeddings(chunks)
            
            # Step 5: Process existing document and add chunks
            document_title = document_filename or "Untitled Document"
            result = await self.insert_document_with_chunks(
                title=document_title,
                document_id=document_id,  # Use existing document ID
                content=preprocessed_content,
                chunks=chunks,
                embeddings=embeddings,
                metadata=metadata,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"PDF processing failed: {str(e)}")
    
    async def ensure_tables_exist(self):
        """Create tables if they don't exist"""
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            raise RuntimeError(f"Failed to create tables: {str(e)}")