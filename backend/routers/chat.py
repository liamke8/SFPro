from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import litellm

from .. import crud, schemas, auth, tasks
from ..database import get_db

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(auth.get_current_user)],
)

@router.post("/completions")
def chat_completion(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Handles a chat request, performs RAG, and returns a response from an LLM.
    """
    # 1. Generate an embedding for the user's message
    query_vector = tasks.model.encode(request.message).tolist()

    # 2. Retrieve relevant context from the database
    similar_pages = crud.search_pages_by_vector(
        db, site_id=request.site_id, vector=query_vector, limit=3
    )

    if not similar_pages:
        context_str = "No relevant context found in the website."
    else:
        # 3. Format the context into a string
        context_str = "Here is some relevant context from the website:\n\n"
        for page in similar_pages:
            context_str += f"--- Page: {page.url} ---\n"
            if page.page_elements and page.page_elements.title:
                context_str += f"Title: {page.page_elements.title}\n"
            if page.page_elements and page.page_elements.h1:
                context_str += f"H1: {page.page_elements.h1}\n"
            # In a real app, you'd include a snippet of the page's markdown content
            context_str += "\n"

    # 4. Construct the prompt for the LLM
    prompt = f"""
    You are a helpful SEO assistant for the website with site ID {request.site_id}.
    A user has asked the following question: "{request.message}"

    Use the following context to answer the user's question. If the context is not sufficient, say that you could not find relevant information on the site.

    Context:
    {context_str}
    """

    messages = [{"role": "user", "content": prompt}]

    # 5. Call the LLM
    try:
        response = litellm.completion(
            model="ollama/llama3", # As specified in the spec
            messages=messages,
            # stream=True # Streaming would be better for a real-time UI
        )
        llm_response = response.choices[0].message.content
        return {"response": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM API call failed: {str(e)}")
