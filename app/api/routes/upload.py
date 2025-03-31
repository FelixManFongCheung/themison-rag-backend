from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse
import io
import asyncio
from typing import List, Dict, Any, Annotated
from app.utils.indexing.database import insert_document
from app.utils.indexing.encoding import encode_doc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from langchain.docstore.document import Document as LangchainDocument
import concurrent.futures
import time

router = APIRouter()

async def process_pdf(file: UploadFile) -> Dict[str, Any]:
    """Process a single PDF file with parallel page extraction."""
    try:
        # Read file content
        content = await file.read()
        filename = file.filename or "unnamed.pdf"
        
        # Create file-like object in memory
        pdf_stream = io.BytesIO(content)
        
        # Try to load the PDF with error handling
        try:
            pdf_reader = PdfReader(pdf_stream)
            total_pages = len(pdf_reader.pages)
            print(f"Total pages: {total_pages}")
        except Exception as e:
            print(f"Error loading PDF: {str(e)}")
            return {
                "originalName": filename,
                "success": False,
                "message": f"Error loading PDF: {str(e)}"
            }
        
        # Extract pages in parallel using ThreadPoolExecutor
        def extract_page(page_num):
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                metadata = {
                    "source": filename,
                    "page": page_num + 1,
                    "total_pages": total_pages
                }
                return LangchainDocument(page_content=text, metadata=metadata)
            except Exception as e:
                print(f"Error extracting page {page_num+1}: {str(e)}")
                # Return a document with minimal content instead of failing
                return LangchainDocument(
                    page_content=f"[Error extracting page {page_num+1}]",
                    metadata={
                        "source": filename,
                        "page": page_num + 1,
                        "total_pages": total_pages,
                        "error": str(e)
                    }
                )
        
        # Use ThreadPoolExecutor for parallel page extraction
        with concurrent.futures.ThreadPoolExecutor() as executor:
            page_nums = range(total_pages)
            pages = list(executor.map(extract_page, page_nums))
        
        # Filter out empty pages if needed
        valid_pages = [p for p in pages if p.page_content and p.page_content != f"[Error extracting page {p.metadata['page']}]"]
        
        if not valid_pages:
            return {
                "originalName": filename,
                "success": False,
                "message": "Could not extract text from any pages in the document"
            }
            
        # Process in batches to avoid memory issues
        batch_size = 20
        all_chunks = 0
        
        print(f"Total valid pages: {len(valid_pages)}")
        
        for i in range(0, len(valid_pages), batch_size):
            page_batch = valid_pages[i:i+batch_size]
            doc_container = encode_doc(page_batch)
            chunks_inserted = await insert_document(doc_container)
            all_chunks += chunks_inserted
        
        return {
            "originalName": filename,
            "success": True,
            "size": len(content),
            "chunks": all_chunks,
            "pages": total_pages,
            "parsed_pages": len(valid_pages)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
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
        print('backend now')
        # Process all files concurrently
        start_time = time.time()
        results = await asyncio.gather(*[process_pdf(file) for file in files])
        end_time = time.time()
        print(f"Time taken to process files: {end_time - start_time:.2f} seconds")
        
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