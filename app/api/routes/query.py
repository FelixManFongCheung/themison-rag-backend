from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.utils.retriever import create_retriever
from app.utils.retrieval_generation.generation import generate_response, call_llm_stream
from fastapi.responses import StreamingResponse

router = APIRouter()

class QueryRequest(BaseModel):
    message: str

@router.post("/")
async def process_query(request: QueryRequest):
    try:
        print('backend now', request)
        user_query = request.message
        retriever = create_retriever(match_count=3)
        results = await retriever(user_query)
        prompt = generate_response(user_query, results)
        
        response = await call_llm_stream(prompt)
        return StreamingResponse(response, media_type="text/event-stream")

    except Exception as e:
        return {"message": f"Error querying documents: {str(e)}"}