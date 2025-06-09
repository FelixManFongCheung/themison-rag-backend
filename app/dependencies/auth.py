from app.lib.supabase_client import supabase_client
from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

supabase = supabase_client()
security = HTTPBearer()

class AuthDependency:
    def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        try:
            user = supabase.auth.get_user(token)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid token")
            return user
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
        
auth = AuthDependency()