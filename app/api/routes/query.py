from fastapi import APIRouter
from pydantic import BaseModel
from app.retrieving_processing.retriever import create_retriever

router = APIRouter()

class Query(BaseModel):
    query: str

@router.post("")
async def query(query: Query):
    try:
        retriever = create_retriever(match_count=3)
        results = await retriever(query.query) 
        return results
    except Exception as e:
        return {"message": f"Error querying documents: {str(e)}"}