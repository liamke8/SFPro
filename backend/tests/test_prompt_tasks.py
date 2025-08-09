import pytest
from unittest.mock import patch, MagicMock

from backend import tasks
from backend.models import Page, PageElement, Template

@patch("backend.tasks.SessionLocal")
@patch("backend.tasks.crud")
@patch("backend.tasks.litellm.completion")
def test_execute_prompt(mock_litellm, mock_crud, mock_session_local):
    # --- Arrange ---
    # Mock the database session and the objects it returns
    mock_db_session = MagicMock()
    mock_session_local.return_value = mock_db_session

    test_page = Page(id=1, url="https://test.com", page_elements=PageElement(title="Test Title", h1="Test H1"))
    test_template = Template(id=1, user_prompt="Generate a title for {h1}", model="ollama/test-model")

    # Configure the mock query to return the correct object based on the filter
    def query_side_effect(model):
        if model == Page:
            q = MagicMock()
            q.filter.return_value.first.return_value = test_page
            return q
        elif model == Template:
            q = MagicMock()
            q.filter.return_value.first.return_value = test_template
            return q
        return MagicMock()
    mock_db_session.query.side_effect = query_side_effect

    # Mock the LLM response
    mock_llm_choice = MagicMock()
    mock_llm_choice.message.content = "Generated Text"
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [mock_llm_choice]
    mock_llm_response.usage.prompt_tokens = 10
    mock_llm_response.usage.completion_tokens = 5
    mock_litellm.return_value = mock_llm_response

    # --- Act ---
    tasks.execute_prompt(page_id=1, template_id=1, run_id=1)

    # --- Assert ---
    # Check that litellm was called correctly
    mock_litellm.assert_called_once()
    args, kwargs = mock_litellm.call_args
    assert kwargs['model'] == "ollama/test-model"
    assert "Generate a title for Test H1" in kwargs['messages'][0]['content']

    # Check that the result was saved to the database
    mock_crud.create_row_generation.assert_called_once()
    args, kwargs = mock_crud.create_row_generation.call_args
    assert kwargs['run_id'] == 1
    assert kwargs['page_id'] == 1
    assert kwargs['output'] == {"generated_text": "Generated Text"}
    assert kwargs['tokens_in'] == 10
    assert kwargs['tokens_out'] == 5

    # Check that the session was closed
    mock_db_session.close.assert_called_once()
