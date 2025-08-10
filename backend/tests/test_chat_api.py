import pytest
from unittest.mock import patch, MagicMock

from backend.routers import chat
from backend.models import Page, PageElement

@patch("litellm.completion")
@patch("backend.crud.search_pages_by_vector")
@patch("backend.tasks.model.encode")
def test_chat_completion(mock_encode, mock_search, mock_litellm):
    # --- Arrange ---
    # Mock the dependencies that are called inside the endpoint function
    mock_db = MagicMock()
    mock_request = chat.schemas.ChatRequest(message="Test message", site_id=1)

    # Mock the return value of the vector search
    mock_page = Page(id=1, url="https://test.com", page_elements=PageElement(title="Test Page Title", h1="Test H1"))
    mock_search.return_value = [mock_page]

    # Mock the return value of the embedding model
    mock_encode.return_value.tolist.return_value = [0.1] * 384

    # Mock the return value of the LLM call
    mock_llm_choice = MagicMock()
    mock_llm_choice.message.content = "This is the LLM response."
    mock_litellm.return_value.choices = [mock_llm_choice]

    # --- Act ---
    result = chat.chat_completion(request=mock_request, db=mock_db)

    # --- Assert ---
    # Check that the search was called
    mock_search.assert_called_once()

    # Check that the LLM was called
    mock_litellm.assert_called_once()
    args, kwargs = mock_litellm.call_args

    # Check that the prompt contains the context from the mocked page
    prompt = kwargs['messages'][0]['content']
    assert "Here is some relevant context" in prompt
    assert "Page: https://test.com" in prompt
    assert "Title: Test Page Title" in prompt
    assert "H1: Test H1" in prompt
    assert 'A user has asked the following question: "Test message"' in prompt

    # Check that the endpoint returns the LLM's response
    assert result == {"response": "This is the LLM response."}
