from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, tasks, auth, models
from ..database import get_db

router = APIRouter(
    prefix="/crawls",
    tags=["crawls"],
    dependencies=[Depends(auth.get_current_user)],
)

@router.post("/", response_model=schemas.Crawl)
def create_crawl(crawl_in: schemas.CrawlCreate, db: Session = Depends(get_db)):
    """
    Initiate a new crawl job for a given site and a list of starting URLs.
    """
    # Optional: Check if the site exists and the user has permission.
    site = crud.get_site(db, site_id=crawl_in.site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Create the crawl job in the database.
    crawl_job = crud.create_crawl_job(
        db=db, site_id=crawl_in.site_id, total_urls=len(crawl_in.urls)
    )

    # Dispatch a Celery task for each URL.
    for url in crawl_in.urls:
        tasks.crawl_page.delay(url=url, site_id=crawl_in.site_id, crawl_id=crawl_job.id)

    return crawl_job
