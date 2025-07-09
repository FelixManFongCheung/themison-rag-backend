from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.api.routes.auth import get_current_user
from app.dependencies.providers import get_embedding_provider
from app.services.retrieval.retrieval_generation_service import \
    RetrievalGenerationService

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