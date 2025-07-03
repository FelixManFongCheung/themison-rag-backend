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
    
    # =================== STEP 1: PDF PARSING ===================
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
    
    # =================== STEP 2: PREPROCESSING ===================
    async def preprocess_content(self, content: str) -> str:
        """Preprocess text content"""
        return preprocess_text(content, clean_whitespace=True)
    
    # =================== STEP 3: CHUNKING ===================
    async def chunk_content(
        self, 
        content: str, 
        metadata: Dict[str, Any] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[LangchainDocument]:
        """Split content into chunks"""
        
        # Create LangChain document
        doc = LangchainDocument(
            page_content=content,
            metadata=metadata or {}
        )
        
        # Use your chunking utility
        chunks = chunk_documents([doc], chunk_size, chunk_overlap)
        return chunks
    
    # =================== STEP 4: EMBEDDING GENERATION ===================
    async def generate_embeddings(self, chunks: List[LangchainDocument]) -> List[List[float]]:
        """Generate embeddings for chunks"""
        
        # Extract text content
        texts = [chunk.page_content for chunk in chunks]
        
        # Use simplified batch processing
        embeddings = self.embedding_provider.get_embeddings_batch(texts)
        
        return embeddings
    
    # =================== STEP 5: DATABASE INSERTION ===================
    async def insert_document_with_chunks(
        self,
        title: str,
        content: str,
        chunks: List[LangchainDocument],
        embeddings: List[List[float]],
        metadata: Dict[str, Any] = None,
        user_id: UUID = None
    ) -> DocumentResponse:
        """Insert document and its chunks into database"""
        
        await self.ensure_tables_exist()
        
        try:
            # 1. Create main document
            document = Document(
                id=uuid4(),
                title=title,
                content=content,
                metadata=metadata or {},
                user_id=user_id,
                created_at=datetime.now(UTC)
            )
                    
            self.db.add(document)
            await self.db.flush()  # Get the document ID
            
            # 2. Insert chunks with embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_record = DocumentChunk(
                    id=uuid4(),
                    document_id=document.id,
                    content=chunk.page_content,
                    chunk_index=i,
                    metadata={**chunk.metadata, "chunk_index": i},
                    embedding=embedding,
                    created_at=datetime.now(UTC)
                )
                self.db.add(chunk_record)
            
            await self.db.commit()
            await self.db.refresh(document)
            
            return DocumentResponse.model_validate(document)
        
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            raise RuntimeError(f"Failed to insert document: {str(e)}")
    
    # =================== COMPLETE PIPELINE ===================
    async def process_pdf_complete(
        self,
        document_url: str,
        user_id: UUID = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> DocumentResponse:
        """Complete PDF processing pipeline"""
        
        try:
            # Step 1: Parse PDF
            content = await self.parse_pdf(document_url)
            document_filename = document_url.split("/")[-1]
            
            # Step 2: Preprocess
            preprocessed_content = await self.preprocess_content(content)
            
            # Step 3: Chunk
            metadata = {"filename": document_filename, "content_type": "application/pdf"}
            chunks = await self.chunk_content(
                preprocessed_content, 
                metadata, 
                chunk_size, 
                chunk_overlap
            )
            
            # Step 4: Generate embeddings
            embeddings = await self.generate_embeddings(chunks)
            
            # Step 5: Insert into database
            document_title = document_filename or "Untitled Document"
            result = await self.insert_document_with_chunks(
                title=document_title,
                content=preprocessed_content,
                chunks=chunks,
                embeddings=embeddings,
                metadata=metadata,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"PDF processing failed: {str(e)}")
    
    # =================== UTILITY METHODS ===================
    async def ensure_tables_exist(self):
        """Create tables if they don't exist"""
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            raise RuntimeError(f"Failed to create tables: {str(e)}")