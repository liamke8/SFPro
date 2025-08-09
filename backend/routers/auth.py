from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

class UserCreate(schemas.OrganizationBase):
    email: str
    password: str
    name: str

@router.post("/signup")
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        supabase_client = auth.get_supabase_client()
        # Step 1: Create the user in Supabase Auth
        auth_response = supabase_client.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
        })
        supabase_user = auth_response.user

        if not supabase_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create user in Supabase")

        # Step 2: Create a default organization for the user
        org_name = f"{user_in.name}'s Organization"
        db_org = crud.create_organization(db, org=schemas.OrganizationCreate(name=org_name))

        # Step 3: Create the user in your local database
        db_user = crud.create_user(db=db, user=schemas.UserCreate(email=user_in.email, name=user_in.name, org_id=db_org.id, role="owner"))

        return {"message": "User created successfully. Please check your email to verify.", "user_id": db_user.id, "org_id": db_org.id}

    except Exception as e:
        # This is a generic error handler. In a real app, you'd want to handle specific Supabase errors.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to sign up: {e}",
        )


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        supabase_client = auth.get_supabase_client()
        auth_response = supabase_client.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password,
        })

        if not auth_response.session:
             raise HTTPException(status_code=400, detail="Incorrect email or password")

        return {"access_token": auth_response.session.access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login failed: {e}",
        )
