from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.retrieval_generation_service import RetrievalGenerationService
from fastapi.responses import StreamingResponse, JSONResponse
from app.api.routes.auth import get_current_user
from app.core.embeddings import get_embedding_provider

router = APIRouter()

class QueryRequest(BaseModel):
    message: str
    retrieve_only: bool = False
    limit: Optional[int] = 5

async def get_rag_service() -> RetrievalGenerationService:
    embedding_provider = get_embedding_provider()
    return RetrievalGenerationService(embedding_provider)

@router.post("/query")
async def process_query(
    request: QueryRequest,
    rag_service: RetrievalGenerationService = Depends(get_rag_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        if request.retrieve_only:
            # Just retrieve documents
            docs = await rag_service.retrieve_documents(request.message, request.limit)
            return JSONResponse(content={"documents": docs})
        else:
            # Full RAG pipeline with streaming response
            generator = await rag_service.process_query(request.message)
            return StreamingResponse(
                generator,
                media_type="text/event-stream"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))