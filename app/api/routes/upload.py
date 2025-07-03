from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.api.routes.auth import get_current_user
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
import requests

router = APIRouter()

class UploadDocumentRequest(BaseModel):
    document_url: str

@router.post("/upload-pdf", response_model=DocumentResponse)
async def upload_pdf_document(
    document_url: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    user = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    """Upload and process PDF document through complete RAG pipeline"""
    
    # Validate file type
    if not document_url.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Process PDF through complete pipeline
        result = await document_service.process_pdf_complete(
            document_url=document_url,
            user_id=user.id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

