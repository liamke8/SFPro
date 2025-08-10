from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, auth, models, tasks
from ..database import get_db

router = APIRouter(
    prefix="/publish",
    tags=["publishing"],
    dependencies=[Depends(auth.get_current_user)],
)

@router.post("/page/{page_id}", status_code=202)
def publish_page(
    page_id: int,
    request: schemas.PublishRequest,
    db: Session = Depends(get_db),
):
    """
    Creates a job to publish content for a page to its integrated CMS.
    """
    # Check if the page exists
    page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # Check if the site has a WP integration
    integration = crud.get_wp_integration_by_site(db, site_id=page.site_id)
    if not integration:
        raise HTTPException(status_code=400, detail="No WordPress integration found for this site.")

    # Create the publish job in the database
    publish_job = crud.create_publish_job(db=db, page_id=page.id, site_id=page.site_id)

    # Dispatch the Celery task
    tasks.publish_to_wordpress.delay(job_id=publish_job.id)

    return {"message": "Publish job created successfully", "job_id": publish_job.id}
