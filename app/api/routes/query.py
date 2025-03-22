from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Query(BaseModel):
    query: str

@router.post("")
async def query(query: Query):
    print(query.query)
    return {"message": f"Query: {query.query}"}