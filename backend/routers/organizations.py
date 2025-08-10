from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/orgs",
    tags=["organizations"],
)

@router.post("/", response_model=schemas.Organization)
def create_organization(org: schemas.OrganizationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # In a real app, you'd check for duplicate names or other business logic.
    return crud.create_organization(db=db, org=org)

@router.get("/", response_model=List[schemas.Organization])
def read_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # This should be scoped to the user's organization in a real app
    organizations = crud.get_organizations(db, skip=skip, limit=limit)
    return organizations

@router.get("/{org_id}", response_model=schemas.Organization)
def read_organization(org_id: int, db: Session = Depends(get_db)):
    db_org = crud.get_organization(db, org_id=org_id)
    if db_org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_org

@router.post("/{org_id}/sites/", response_model=schemas.Site)
def create_site_for_organization(
    org_id: int, site: schemas.SiteCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)
):
    # Here you should also check if the current_user belongs to the org_id
    db_org = crud.get_organization(db, org_id=org_id)
    if not db_org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.create_site_for_organization(db=db, site=site, org_id=org_id)

@router.get("/{org_id}/sites/", response_model=List[schemas.Site])
def read_sites_for_organization(
    org_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)
):
    # Here you should also check if the current_user belongs to the org_id
    db_org = crud.get_organization(db, org_id=org_id)
    if not db_org:
        raise HTTPException(status_code=404, detail="Organization not found")
    sites = crud.get_sites_by_organization(db=db, org_id=org_id, skip=skip, limit=limit)
    return sites
