from fastapi.testclient import TestClient

from backend import models
from backend.main import app
from backend.auth import get_current_user

def test_template_crud_api(client: TestClient, db_session, test_user):
    # --- Arrange ---
    # Override the auth dependency
    def get_test_user_override():
        return test_user
    app.dependency_overrides[get_current_user] = get_test_user_override

    # --- Act & Assert: Create ---
    template_data = {
        "name": "Test Title Generator",
        "system_prompt": "You are an SEO expert.",
        "user_prompt": "Generate a title for a page with the following H1: {h1}",
        "org_id": test_user.org_id,
    }
    response = client.post("/api/templates/", json=template_data)
    assert response.status_code == 200
    created_template = response.json()
    assert created_template["name"] == "Test Title Generator"
    assert created_template["org_id"] == test_user.org_id
    template_id = created_template["id"]

    # --- Act & Assert: Read Single ---
    response = client.get(f"/api/templates/{template_id}")
    assert response.status_code == 200
    read_template = response.json()
    assert read_template["name"] == "Test Title Generator"

    # --- Act & Assert: Read by Organization ---
    response = client.get(f"/api/templates/org/{test_user.org_id}")
    assert response.status_code == 200
    templates_list = response.json()
    assert len(templates_list) == 1
    assert templates_list[0]["name"] == "Test Title Generator"
