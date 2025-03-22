from fastapi import APIRouter
from app.database import insert_documents
router = APIRouter()

@router.post("/upload")
async def upload_documents():
    try:
        await insert_documents()
        return {"message": "Documents uploaded successfully"}
    except Exception as e:
        return {"message": f"Error uploading documents: {str(e)}"}