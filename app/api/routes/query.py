from fastapi import APIRouter

router = APIRouter()

@router.get("/query")
async def query():
    return {"message": "Hello, World!"}