import pytest
from unittest.mock import patch, MagicMock
import numpy as np

from backend import tasks
from backend.models import Page, PageElement

@patch("backend.tasks.SessionLocal")
@patch("backend.tasks.crud")
@patch("backend.tasks.model")
def test_generate_embeddings(mock_model, mock_crud, mock_session_local):
    # --- Arrange ---
    # Mock the database session and the page object it returns
    mock_db_session = MagicMock()
    mock_session_local.return_value = mock_db_session

    test_page = Page(id=1, page_elements=PageElement(title="Test Title", h1="Test H1"))
    mock_db_session.query.return_value.filter.return_value.first.return_value = test_page

    # Mock the embedding model
    dummy_vector = np.array([0.1, 0.2, 0.3]).tolist()
    mock_model.encode.return_value.tolist.return_value = dummy_vector

    # --- Act ---
    tasks.generate_embeddings(page_id=1)

    # --- Assert ---
    # Check that the model was called for title and h1
    assert mock_model.encode.call_count == 2
    mock_model.encode.assert_any_call("Test Title")
    mock_model.encode.assert_any_call("Test H1")

    # Check that the CRUD function was called to save the embeddings
    assert mock_crud.create_embedding.call_count == 2
    mock_crud.create_embedding.assert_any_call(
        mock_db_session, page_id=1, kind="title", vector=dummy_vector
    )
    mock_crud.create_embedding.assert_any_call(
        mock_db_session, page_id=1, kind="h1", vector=dummy_vector
    )

    # Check that the session was closed
    mock_db_session.close.assert_called_once()
