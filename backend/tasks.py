import json
import litellm
from bs4 import BeautifulSoup
from readability import Document
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from sentence_transformers import SentenceTransformer

from .celery_app import celery_app
from . import crud
from .database import SessionLocal
from .models import Page, Template

# Load the sentence transformer model once per worker
model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_seo_data(soup, url):
    """Extracts various SEO elements from a BeautifulSoup object."""
    # ... (rest of the function is the same)
    def get_text(element, default=""):
        return element.get_text(strip=True) if element else default
    def get_attr(element, attr, default=""):
        return element.get(attr, default) if element else default
    title = get_text(soup.find('title'))
    meta_description = get_attr(soup.find('meta', attrs={'name': 'description'}), 'content')
    canonical_url = get_attr(soup.find('link', rel='canonical'), 'href')
    meta_robots = get_attr(soup.find('meta', attrs={'name': 'robots'}), 'content')
    h1 = get_text(soup.find('h1'))
    h2s = [get_text(h2) for h2 in soup.find_all('h2')]
    og_tags = { prop.get('property'): prop.get('content') for prop in soup.find_all('meta', property=lambda x: x and x.startswith('og:')) }
    twitter_tags = { name.get('name'): name.get('content') for name in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}) }
    schema_ld_json = [ json.loads(script.string) for script in soup.find_all('script', type='application/ld+json') if script.string ]
    links = [{"href": get_attr(a, 'href'), "text": get_text(a)} for a in soup.find_all('a', href=True)]
    images = [{"src": get_attr(img, 'src'), "alt": get_attr(img, 'alt')} for img in soup.find_all('img')]
    return { "url": url, "title": title, "meta_description": meta_description, "canonical_url": canonical_url, "meta_robots": meta_robots, "h1": h1, "h2s": h2s, "og_tags": og_tags, "twitter_tags": twitter_tags, "schema_ld_json": schema_ld_json, "links": links, "images": images }


@celery_app.task
def execute_prompt(page_id: int, template_id: int, run_id: int):
    """
    Executes a prompt template on a given page's data.
    """
    print(f"Executing prompt for page {page_id}, template {template_id}")
    db = SessionLocal()
    try:
        page = db.query(Page).filter(Page.id == page_id).first()
        template = db.query(Template).filter(Template.id == template_id).first()

        if not page or not template:
            raise ValueError("Page or Template not found")

        # Assemble context from page data
        context = {
            "url": page.url,
            "title": page.page_elements.title,
            "h1": page.page_elements.h1,
            "description": page.page_elements.description,
            # TODO: Add markdown content and other fields
        }

        # Replace variables in the user prompt
        prompt_text = template.user_prompt.format(**context)

        messages = [{"role": "user", "content": prompt_text}]
        if template.system_prompt:
            messages.insert(0, {"role": "system", "content": template.system_prompt})

        # Call the LLM using litellm
        response = litellm.completion(model=template.model, messages=messages)

        output_content = response.choices[0].message.content
        output_data = {"generated_text": output_content} # TODO: Handle JSON output schema

        # Save the result
        crud.create_row_generation(
            db=db,
            run_id=run_id,
            page_id=page_id,
            input_context=context,
            output=output_data,
            tokens_in=response.usage.prompt_tokens,
            tokens_out=response.usage.completion_tokens,
        )
        print(f"Successfully executed prompt for page {page_id}")

    except Exception as e:
        print(f"Error executing prompt for page {page_id}: {e}")
        # TODO: Update PromptRun status to 'failed'
    finally:
        db.close()


@celery_app.task
def generate_embeddings(page_id: int):
    # ... (implementation is the same)
    print(f"Generating embeddings for page {page_id}")
    db = SessionLocal()
    try:
        page = db.query(Page).filter(Page.id == page_id).first()
        if not page or not page.page_elements:
            print(f"Page {page_id} or its elements not found.")
            return
        if page.page_elements.title:
            title_vector = model.encode(page.page_elements.title).tolist()
            crud.create_embedding(db, page_id=page_id, kind="title", vector=title_vector)
        if page.page_elements.h1:
            h1_vector = model.encode(page.page_elements.h1).tolist()
            crud.create_embedding(db, page_id=page_id, kind="h1", vector=h1_vector)
        print(f"Successfully generated embeddings for page {page_id}")
    except Exception as e:
        print(f"Error generating embeddings for page {page_id}: {e}")
    finally:
        db.close()


@celery_app.task
def crawl_page(url: str, site_id: int, crawl_id: int):
    # ... (implementation is the same)
    print(f"Crawling {url} for site {site_id} (crawl job {crawl_id})")
    db = SessionLocal()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            response = page.goto(url, timeout=30000)
            status_code = response.status if response else None
            if not status_code or status_code >= 400:
                browser.close()
                return {"url": url, "error": f"HTTP status code: {status_code}"}
            html_content = page.content()
            browser.close()
            doc = Document(html_content)
            clean_html = doc.summary()
            full_soup = BeautifulSoup(html_content, 'html.parser')
            seo_data = extract_seo_data(full_soup, url)
            page_data = { "status_code": status_code, "clean_html": clean_html }
            created_page = crud.create_page_with_elements(db=db, page_data=page_data, seo_data=seo_data, site_id=site_id)
            generate_embeddings.delay(page_id=created_page.id)
            return { "status": "success", "url": url, "message": "Page crawled and data saved successfully." }
    except PlaywrightTimeoutError:
        return {"url": url, "error": "Navigation timed out."}
    except Exception as e:
        return {"url": url, "error": f"An unexpected error occurred: {str(e)}"}
    finally:
        db.close()

@celery_app.task
def add(x, y):
    """A simple task to test the Celery setup."""
    return x + y
