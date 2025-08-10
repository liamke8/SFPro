from unittest.mock import patch
from fastapi.testclient import TestClient

from backend import models, schemas
from backend.main import app
from backend.auth import get_current_user

def test_run_prompt_api(client: TestClient, db_session, test_user):
    # --- Arrange ---
    # Override auth
    def get_test_user_override():
        return test_user
    app.dependency_overrides[get_current_user] = get_test_user_override

    # Create a site, page, and template
    site = models.Site(domain="test-prompt-site.com", org_id=test_user.org_id)
    db_session.add(site)
    db_session.commit()

    page = models.Page(url="https://test-prompt-site.com/page1", site_id=site.id)
    db_session.add(page)
    db_session.commit()

    template = models.Template(
        name="Test Prompt Template",
        user_prompt="Test prompt",
        org_id=test_user.org_id,
    )
    db_session.add(template)
    db_session.commit()

    # Mock the Celery task
    with patch("backend.tasks.execute_prompt.delay") as mock_celery_task:
        # --- Act ---
        response = client.post(
            f"/api/prompts/run/page/{page.id}",
            json={"template_id": template.id},
        )

        # --- Assert ---
        assert response.status_code == 200
        data = response.json()
        assert data["template_id"] == template.id
        assert data["user_id"] == test_user.id
        assert data["status"] == "starting"

        # Check that the Celery task was called
        mock_celery_task.assert_called_once_with(
            page_id=page.id, template_id=template.id, run_id=data["id"]
        )
