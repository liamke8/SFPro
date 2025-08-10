from fastapi.testclient import TestClient

from backend import models
from backend.main import app
from backend.auth import get_current_user

def test_export_site_csv(client: TestClient, db_session, test_user):
    # --- Arrange ---
    # Auth override
    def get_test_user_override():
        return test_user
    app.dependency_overrides[get_current_user] = get_test_user_override

    # Create a site and a page with elements
    site = models.Site(domain="test-export-site.com", org_id=test_user.org_id)
    db_session.add(site)
    db_session.commit()

    page = models.Page(url="https://test-export-site.com/page1", site_id=site.id, status_code=200)
    db_session.add(page)
    db_session.commit()

    elements = models.PageElement(
        page_id=page.id,
        title="Test Export Title",
        description="Test Export Desc",
        h1="Test Export H1"
    )
    db_session.add(elements)
    db_session.commit()

    # --- Act ---
    response = client.get(f"/api/export/site/{site.id}/csv")

    # --- Assert ---
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=" in response.headers["content-disposition"]

    # Check the content of the CSV
    content = response.content.decode("utf-8")
    lines = content.strip().split('\n')
    assert len(lines) == 2 # Header + 1 row

    header = lines[0].strip()
    row = lines[1].strip()

    assert header == "URL,Status Code,Title,Meta Description,H1"
    assert row == "https://test-export-site.com/page1,200,Test Export Title,Test Export Desc,Test Export H1"
