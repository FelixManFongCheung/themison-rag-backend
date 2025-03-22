from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse
import io
import asyncio
from typing import List, Dict, Any, Annotated
from app.database import insert_document
from app.encoding import encode_doc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from langchain.docstore.document import Document as LangchainDocument

router = APIRouter()

async def process_pdf(file: UploadFile) -> Dict[str, Any]:
    """Process a single PDF file and return the results."""
    print('document processing')
    try:
        # Read file content
        content = await file.read()
        filename = file.filename or "unnamed.pdf"
        
        # Create file-like object in memory
        pdf_stream = io.BytesIO(content)
        
        # 1. Load the PDF
        pdf_reader = PdfReader(pdf_stream)
        pages = []
        
        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            metadata = {
                "source": filename,
                "page": i + 1,
                "total_pages": len(pdf_reader.pages)
            }
            pages.append(LangchainDocument(page_content=text, metadata=metadata))
        
        doc_container = encode_doc(pages)
        # 5. Insert into database
        total_chunks = await insert_document(doc_container)
        
        return {
            "originalName": filename,
            "success": True,
            "size": len(content),
            "chunks": total_chunks,
            "pages": len(pdf_reader.pages)
        }
        
    except Exception as e:
        return {
            "originalName": getattr(file, "filename", "unknown"),
            "success": False,
            "message": f"Error processing file: {str(e)}"
        }

@router.post("/upload")
async def upload_documents(
    files: Annotated[List[UploadFile], File(description="Multiple PDF files")]
):
    try:
        # Process all files concurrently
        results = await asyncio.gather(*[process_pdf(file) for file in files])
        
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
            "files": results
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