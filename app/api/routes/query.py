from fastapi import APIRouter
from pydantic import BaseModel
from app.query_processing.retriever import create_retriever

router = APIRouter()

class Query(BaseModel):
    query: str

@router.post("")
async def query(query: Query):
    retriever = create_retriever(match_count=3, alpha=0.5)
    results = await retriever(query.query) 
    return results