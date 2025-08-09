from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/templates",
    tags=["templates"],
    dependencies=[Depends(auth.get_current_user)],
)

@router.post("/", response_model=schemas.Template)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(get_db)):
    # TODO: Check if user belongs to the org.
    return crud.create_template(db=db, template=template)

@router.get("/{template_id}", response_model=schemas.Template)
def read_template(template_id: int, db: Session = Depends(get_db)):
    db_template = crud.get_template(db, template_id=template_id)
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    # TODO: Check if user has permission to access this template.
    return db_template

@router.get("/org/{org_id}", response_model=List[schemas.Template])
def read_templates_for_organization(org_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # TODO: Check if user belongs to the org.
    templates = crud.get_templates_by_organization(db, org_id=org_id, skip=skip, limit=limit)
    return templates
