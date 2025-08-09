from fastapi.testclient import TestClient

from backend import models
from backend.main import app
from backend.auth import get_current_user

def test_read_site_pages(client: TestClient, db_session, test_user):
    # --- Arrange ---
    # Override the auth dependency
    def get_test_user_override():
        return test_user
    app.dependency_overrides[get_current_user] = get_test_user_override

    # Create a site and some pages for the test user's organization
    site = models.Site(domain="site-with-pages.com", org_id=test_user.org_id)
    db_session.add(site)
    db_session.commit()

    for i in range(5):
        page = models.Page(url=f"https://site-with-pages.com/page{i}", site_id=site.id, status_code=200)
        db_session.add(page)
    db_session.commit()

    # --- Act ---
    response = client.get(f"/api/sites/{site.id}/pages?page=1&size=3")

    # --- Assert ---
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 5
    assert data["page"] == 1
    assert data["size"] == 3
    assert len(data["items"]) == 3
    assert data["items"][0]["url"] == "https://site-with-pages.com/page0"
