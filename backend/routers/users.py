from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_current_user)],
)

@router.get("/me", response_model=schemas.User)
def read_users_me(
    db: Session = Depends(get_db),
    current_supabase_user = Depends(auth.get_current_user)
):
    """
    Get the current logged-in user's details from the local database.
    """
    db_user = crud.get_user_by_supabase_id(db, supabase_id=current_supabase_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found in local database")
    return db_user
