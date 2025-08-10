import pytest
from unittest.mock import patch, MagicMock

from backend import tasks
from backend.database import SessionLocal

@pytest.fixture
def sample_html():
    with open("backend/tests/sample_page.html", "r") as f:
        return f.read()

@patch("backend.tasks.generate_embeddings.delay")
@patch("backend.tasks.sync_playwright")
@patch("backend.crud.create_page_with_elements")
def test_crawl_page_success(mock_create_page, mock_sync_playwright, mock_generate_embeddings, sample_html):
    # --- Arrange ---
    # Mock the CRUD function to return a mock page with an ID
    mock_create_page.return_value = MagicMock(id=1)

    # Mock Playwright to avoid real network calls
    mock_page = MagicMock()
    mock_page.content.return_value = sample_html
    mock_page.goto.return_value.status = 200
    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_playwright_context = MagicMock()
    mock_playwright_context.chromium.launch.return_value = mock_browser
    mock_sync_playwright.return_value.__enter__.return_value = mock_playwright_context

    # --- Act ---
    # Call the task directly as a function to unit test its logic
    result = tasks.crawl_page(url="https://example.com/sample-page", site_id=1, crawl_id=1)

    # --- Assert ---
    assert result["status"] == "success"

    # Check that the CRUD function was called once
    mock_create_page.assert_called_once()

    # Inspect the arguments passed to the mocked CRUD function
    args, kwargs = mock_create_page.call_args
    db_session = kwargs.get('db')
    page_data = kwargs.get('page_data')
    seo_data = kwargs.get('seo_data')

    assert db_session is not None
    assert page_data['status_code'] == 200

    # Assertions for extracted SEO data
    assert seo_data['title'] == "Sample Test Page"
    assert seo_data['meta_description'] == "This is a sample description for testing."
    assert seo_data['canonical_url'] == "https://example.com/sample-page"
    assert seo_data['h1'] == "Main H1 Heading"
    assert seo_data['h2s'] == ["First H2 Subheading", "Second H2 Subheading"]
    assert seo_data['og_tags']['og:title'] == "Open Graph Title"
    assert len(seo_data['links']) == 1
    assert seo_data['links'][0]['text'] == "Internal Link"
    assert len(seo_data['images']) == 1
    assert seo_data['images'][0]['alt'] == "Sample Image Alt Text"
    assert seo_data['schema_ld_json'][0]['@type'] == "WebPage"

    # Check that the embedding task was called
    mock_generate_embeddings.assert_called_once_with(page_id=1)
