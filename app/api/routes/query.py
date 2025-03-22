from fastapi import APIRouter
from pydantic import BaseModel
from app.retrieving_processing.retriever import create_retriever
from app.generating_processing.generation import generate_response, call_llm
router = APIRouter()

class Query(BaseModel):
    query: str

@router.post("")
async def query(query: Query):
    try:
        retriever = create_retriever(match_count=3)
        results = await retriever(query.query) 
        prompt = generate_response(query.query, results)
        response = await call_llm(prompt)
        return response
    except Exception as e:
        return {"message": f"Error querying documents: {str(e)}"}