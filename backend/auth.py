from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
from typing import Optional

from .config import settings
from .database import get_db
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Lazily initializes and returns a Supabase client.
    This prevents the client from being created at import time, which is useful for testing.
    """
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase credentials are not set in the environment.")
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current user from a JWT token.
    """
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        supabase_user = user_response.user
        if not supabase_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # In a real app, you would fetch the user from your own database here
        # using the supabase_user.id or email to link the accounts.
        # For now, we return the Supabase user object directly.
        return supabase_user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
