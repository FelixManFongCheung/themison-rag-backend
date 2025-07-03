from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.api.routes.auth import get_current_user
from fastapi.responses import JSONResponse
import io
import asyncio
from typing import List, Dict, Any, Annotated
from app.services.indexing.utils.database import insert_document
from app.services.indexing.utils.encoding import encode_doc
from pypdf import PdfReader
from langchain.docstore.document import Document as LangchainDocument
import concurrent.futures
from datetime import datetime
from pydantic import BaseModel
import requests

router = APIRouter()

class UploadDocumentRequest(BaseModel):
    document_url: str

@router.post("/upload-document")
async def upload_document(
    request: UploadDocumentRequest,
    user = Depends(get_current_user)
):
    try:
        document_url = request.document_url
        file = await download_file(document_url)
        
        results = await asyncio.gather(*[
            process_pdf(file, user.id) for file in files
        ])
        
        # Calculate total successful chunks
        total_chunks = sum(
            result.get("chunks", 0) 
            for result in results 
            if result.get("success", False)
        )
        
        # Count successful files
        successful_files = sum(1 for result in results if result.get("success", False))
        
        return {
            "success": True,
            "message": f"Successfully processed {successful_files}/{len(files)} files with {total_chunks} total chunks inserted.",
            "files": results,
            "user_id": user.id
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error uploading documents: {str(e)}"
            }
        )

