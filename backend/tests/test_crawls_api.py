from unittest.mock import patch
from fastapi.testclient import TestClient

from backend import models
from backend.main import app
from backend.auth import get_current_user

def test_create_crawl_api(client: TestClient, db_session, test_user):
    # --- Arrange ---
    # Override the auth dependency to return our test user
    def get_test_user_override():
        return test_user
    app.dependency_overrides[get_current_user] = get_test_user_override

    # Create a site for the test user's organization
    site = models.Site(domain="testsite.com", org_id=test_user.org_id)
    db_session.add(site)
    db_session.commit()

    # Mock the Celery task
    with patch("backend.tasks.crawl_page.delay") as mock_celery_task:
        # --- Act ---
        response = client.post(
            "/api/crawls/",
            json={"site_id": site.id, "urls": ["https://testsite.com/page1", "https://testsite.com/page2"]},
        )

        # --- Assert ---
        assert response.status_code == 200
        data = response.json()
        assert data["site_id"] == site.id
        assert data["status"] == "starting"
        assert data["total_pages"] == 2

        # Check that the Celery task was called twice
        assert mock_celery_task.call_count == 2
        mock_celery_task.assert_any_call(url="https://testsite.com/page1", site_id=site.id, crawl_id=data["id"])
        mock_celery_task.assert_any_call(url="https://testsite.com/page2", site_id=site.id, crawl_id=data["id"])
