from fastapi import APIRouter
# from app.database import insert_documents
router = APIRouter()

@router.post("/upload")
async def upload_documents():
    
    return {"message": "Hello, World!"}

@router.get("/list")
def list_documents():
    return {"message": "Hello, World!"}