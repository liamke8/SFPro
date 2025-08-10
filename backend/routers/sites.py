from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas, auth, tasks
from ..database import get_db

router = APIRouter(
    prefix="/sites",
    tags=["sites"],
    dependencies=[Depends(auth.get_current_user)],
)

@router.get("/{site_id}", response_model=schemas.Site)
def read_site(site_id: int, db: Session = Depends(get_db)):
    db_site = crud.get_site(db, site_id=site_id)
    if db_site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    # TODO: Check if user has permission to access this site.
    return db_site

@router.get("/{site_id}/pages", response_model=schemas.PaginatedResponse[schemas.Page])
def read_site_pages(
    site_id: int,
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 100,
):
    # TODO: Check if user has permission to access this site.
    site = crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    skip = (page - 1) * size
    result = crud.get_pages_by_site(db, site_id=site_id, skip=skip, limit=size)

    return {
        "items": result["items"],
        "total": result["total"],
        "page": page,
        "size": size,
    }

@router.post("/{site_id}/search", response_model=List[schemas.Page])
def search_site_pages(
    site_id: int,
    request: schemas.SearchRequest,
    db: Session = Depends(get_db),
):
    """
    Search for pages within a site using vector similarity search.
    """
    # TODO: Check user permissions for the site.
    site = crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Generate embedding for the query
    query_vector = tasks.model.encode(request.query).tolist()

    # Perform the search
    pages = crud.search_pages_by_vector(db, site_id=site_id, vector=query_vector, limit=request.limit)

    return pages
