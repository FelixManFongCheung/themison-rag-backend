from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.dependencies.auth import get_current_user
from fastapi.responses import JSONResponse
import io
import asyncio
from typing import List, Dict, Any, Annotated
from app.services.indexing.document_service import DocumentService
from app.dependencies.rag import get_document_service
from app.contracts.document import DocumentResponse
from pypdf import PdfReader
from langchain.docstore.document import Document as LangchainDocument
import concurrent.futures
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
import requests

router = APIRouter()

class UploadDocumentRequest(BaseModel):
    document_url: str
    document_id: UUID

@router.post("/upload-pdf", response_model=DocumentResponse)
async def upload_pdf_document(
    document_url: str,
    document_id: UUID,  # UUID of existing document created by frontend
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    user = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Process existing PDF document for RAG (Retrieval-Augmented Generation)
    
    Hybrid workflow:
    1. Frontend uploads document directly to database (creates document record)
    2. Frontend sends document_id + document_url to this endpoint  
    3. Backend downloads PDF, processes it (chunks + embeddings)
    4. Backend stores chunks that reference the existing document_id
    """
    
    # Validate file type
    if not document_url.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Process existing document through RAG pipeline
        result = await document_service.process_pdf_complete(
            document_url=document_url,
            document_id=document_id,  # Reference existing document
            user_id=user["id"],  # Fixed: user is dict, not object
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        return result
        
    except ValueError as e:
        # Document not found or validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Processing or database errors
        raise HTTPException(status_code=500, detail=str(e))

