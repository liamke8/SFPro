import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import crud, auth
from ..database import get_db

router = APIRouter(
    prefix="/export",
    tags=["export"],
    dependencies=[Depends(auth.get_current_user)],
)

@router.get("/site/{site_id}/csv")
def export_site_to_csv(site_id: int, db: Session = Depends(get_db)):
    """
    Exports all page data for a given site to a CSV file.
    """
    # TODO: Check user permissions for the site.
    site = crud.get_site(db, site_id=site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    pages = crud.get_all_pages_for_site(db, site_id=site_id)

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    header = ["URL", "Status Code", "Title", "Meta Description", "H1"]
    writer.writerow(header)

    # Write rows
    for page in pages:
        row = [
            page.url,
            page.status_code,
            page.page_elements.title if page.page_elements else "",
            page.page_elements.description if page.page_elements else "",
            page.page_elements.h1 if page.page_elements else "",
        ]
        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=site_{site_id}_export.csv"},
    )
