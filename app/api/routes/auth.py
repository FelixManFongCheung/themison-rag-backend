from fastapi import APIRouter, Depends

from app.dependencies.auth import auth

router = APIRouter()

@router.get("/me")
async def get_current_user(user = Depends(auth.verify_jwt)):
    return user
