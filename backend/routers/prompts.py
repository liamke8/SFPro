from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, auth, models, tasks
from ..database import get_db

router = APIRouter(
    prefix="/prompts",
    tags=["prompts"],
    dependencies=[Depends(auth.get_current_user)],
)

@router.post("/run/page/{page_id}", response_model=schemas.PromptRun)
def run_prompt_on_page(
    page_id: int,
    request: schemas.RunPromptRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Initiate a prompt execution job for a given page and template.
    """
    # Check if page and template exist
    page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    template = crud.get_template(db, template_id=request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # TODO: Check user permissions for page and template.

    # Create the prompt run job
    prompt_run = crud.create_prompt_run(
        db=db, template_id=request.template_id, user_id=current_user.id
    )

    # Dispatch the Celery task
    tasks.execute_prompt.delay(
        page_id=page_id, template_id=request.template_id, run_id=prompt_run.id
    )

    return prompt_run
