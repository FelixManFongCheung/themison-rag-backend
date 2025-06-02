from fastapi import APIRouter, Depends, HTTPException
from app.services.interfaces.document_service import IDocumentService
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.dependencies.services import get_document_service
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=DocumentResponse)
async def create_document(
    doc: DocumentCreate,
    service: IDocumentService = Depends(get_document_service)
) -> DocumentResponse:
    return await service.create(doc)

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: UUID,
    service: IDocumentService = Depends(get_document_service)
) -> DocumentResponse:
    try:
        return await service.get(doc_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    service: IDocumentService = Depends(get_document_service)
) -> List[DocumentResponse]:
    return await service.list()

@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: UUID,
    doc: DocumentUpdate,
    service: IDocumentService = Depends(get_document_service)
) -> DocumentResponse:
    try:
        return await service.update(doc_id, doc)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: UUID,
    service: IDocumentService = Depends(get_document_service)
):
    try:
        await service.delete(doc_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/search/{query}", response_model=List[DocumentResponse])
async def search_documents(
    query: str,
    service: IDocumentService = Depends(get_document_service)
) -> List[DocumentResponse]:
    return await service.search(query) 