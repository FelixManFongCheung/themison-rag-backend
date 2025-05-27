from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.utils.retriever import create_retriever
from app.utils.retrieval_generation.generation import generate_response, call_llm_stream
from fastapi.responses import StreamingResponse, JSONResponse
from app.api.routes.auth import get_current_user

router = APIRouter()

class QueryRequest(BaseModel):
    message: str

@router.post("/")
async def process_query(
    request: QueryRequest,
    user = Depends(get_current_user)
):
    try:
        user_query = request.message
        retriever = create_retriever(
            match_count=3,
            user_id=user.id
        )
        
        results = await retriever(user_query)
        
        prompt = generate_response(
            user_query,
            results,
            user_context={"user_id": user.id}
        )
        
        response = await call_llm_stream(prompt)
        return StreamingResponse(response, media_type="text/event-stream")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error querying documents: {str(e)}"
            }
        )