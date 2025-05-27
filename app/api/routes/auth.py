from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.lib.supabase_client import supabase_client
from datetime import datetime

router = APIRouter()
security = HTTPBearer()
supabase = supabase_client()

# Request Models
class UserAuthRequest(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

# Response Models
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime
    last_sign_in: Optional[datetime] = None

class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = await supabase.auth.get_user(credentials.credentials)
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

# Auth Routes
@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserAuthRequest):
    """
    Register a new user with email and password
    """
    try:
        auth_response = await supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if auth_response.user and auth_response.session:
            return {
                "user": auth_response.user,
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to create user"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login", response_model=AuthResponse)
async def login(user_data: UserAuthRequest):
    """
    Authenticate existing user with email and password
    """
    try:
        auth_response = await supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        return {
            "user": auth_response.user,
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

@router.post("/logout")
async def logout(user = Depends(get_current_user)):
    """
    Sign out the current user
    """
    try:
        await supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to logout"
        )

@router.post("/refresh-token")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token using refresh token
    """
    try:
        response = await supabase.auth.refresh_session()
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user = Depends(get_current_user)):
    """
    Get current user information
    """
    return user

@router.post("/reset-password")
async def reset_password(email: EmailStr):
    """
    Send password reset email
    """
    try:
        await supabase.auth.reset_password_email(email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Failed to send reset email"
        )

# Protected routes example
@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    user = Depends(get_current_user)
):
    """
    Update user profile (protected route example)
    """
    try:
        response = await supabase.table('profiles')\
            .update(profile_data.dict(exclude_none=True))\
            .eq('id', user.id)\
            .execute()
            
        return response.data[0]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to update profile"
        )
