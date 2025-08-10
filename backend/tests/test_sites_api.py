from unittest.mock import patch, ANY
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

@patch("backend.crud.search_pages_by_vector")
def test_search_site_pages(mock_search_crud, client: TestClient, db_session, test_user):
    # --- Arrange ---
    # Auth override
    def get_test_user_override():
        return test_user
    app.dependency_overrides[get_current_user] = get_test_user_override

    # Create a site and a page
    site = models.Site(domain="test-search-site.com", org_id=test_user.org_id)
    db_session.add(site)
    db_session.commit()

    page_to_find = models.Page(url="https://test-search-site.com/page-to-find", site_id=site.id)
    db_session.add(page_to_find)
    db_session.commit()

    # Configure the mock CRUD function to return our test page
    mock_search_crud.return_value = [page_to_find]

    # Mock the sentence transformer model
    with patch("backend.tasks.model.encode") as mock_encode:
        query_vector = [0.1] * 384
        mock_encode.return_value.tolist.return_value = query_vector

        # --- Act ---
        response = client.post(
            f"/api/sites/{site.id}/search",
            json={"query": "test query", "limit": 5},
        )

        # --- Assert ---
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == page_to_find.id

        mock_encode.assert_called_once_with("test query")

        # Assert that the mock was called, then check args individually
        mock_search_crud.assert_called_once()
        call_args, call_kwargs = mock_search_crud.call_args
        assert call_kwargs.get("site_id") == site.id
        assert call_kwargs.get("limit") == 5
        assert isinstance(call_kwargs.get("vector"), list)
        assert len(call_kwargs.get("vector")) == 384
