from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend import models, tasks
from backend.main import app
from backend.auth import get_current_user

def test_publish_page_api(client: TestClient, db_session, test_user):
    # --- Arrange ---
    # Auth override
    def get_test_user_override():
        return test_user
    app.dependency_overrides[get_current_user] = get_test_user_override

    # Create a site, page, and integration
    site = models.Site(domain="test-publish-site.com", org_id=test_user.org_id)
    db_session.add(site)
    db_session.commit()

    page = models.Page(url="https://test-publish-site.com/page1", site_id=site.id)
    db_session.add(page)
    db_session.commit()

    integration = models.WordpressIntegration(site_id=site.id, base_url="https://test-publish-site.com", api_key="key")
    db_session.add(integration)
    db_session.commit()

    # Mock the Celery task
    with patch("backend.tasks.publish_to_wordpress.delay") as mock_celery_task:
        # --- Act ---
        response = client.post(f"/api/publish/page/{page.id}", json={})

        # --- Assert ---
        assert response.status_code == 202
        data = response.json()
        assert data["message"] == "Publish job created successfully"
        job_id = data["job_id"]

        # Check that a PublishJob was created
        job = db_session.query(models.PublishJob).filter(models.PublishJob.id == job_id).first()
        assert job is not None
        assert job.status == "pending"

        # Check that the Celery task was called
        mock_celery_task.assert_called_once_with(job_id=job_id)

@patch("backend.tasks.SessionLocal")
def test_publish_to_wordpress_task(mock_session_local):
    # --- Arrange ---
    mock_db_session = MagicMock()
    mock_session_local.return_value = mock_db_session

    mock_job = models.PublishJob(id=1, status="pending")
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_job

    # --- Act ---
    tasks.publish_to_wordpress(job_id=1)

    # --- Assert ---
    # Check that the job status was updated to completed
    assert mock_job.status == "completed"
    mock_db_session.commit.assert_called_once()
    mock_db_session.close.assert_called_once()
