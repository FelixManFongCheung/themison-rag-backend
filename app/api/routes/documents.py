from fastapi import APIRouter
from app.database import insert_documents
router = APIRouter()

@router.post("/documents/upload")
async def upload_documents():
    
    return {"message": "Hello, World!"}