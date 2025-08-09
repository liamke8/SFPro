import json
from bs4 import BeautifulSoup
from readability import Document
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from .celery_app import celery_app
from . import crud
from .database import SessionLocal

def extract_seo_data(soup, url):
    """Extracts various SEO elements from a BeautifulSoup object."""

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

    og_tags = {
        prop.get('property'): prop.get('content')
        for prop in soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
    }

    twitter_tags = {
        name.get('name'): name.get('content')
        for name in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
    }

    schema_ld_json = [
        json.loads(script.string)
        for script in soup.find_all('script', type='application/ld+json')
        if script.string
    ]

    links = [{"href": get_attr(a, 'href'), "text": get_text(a)} for a in soup.find_all('a', href=True)]
    images = [{"src": get_attr(img, 'src'), "alt": get_attr(img, 'alt')} for img in soup.find_all('img')]

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "canonical_url": canonical_url,
        "meta_robots": meta_robots,
        "h1": h1,
        "h2s": h2s,
        "og_tags": og_tags,
        "twitter_tags": twitter_tags,
        "schema_ld_json": schema_ld_json,
        "links": links,
        "images": images,
    }

@celery_app.task
def crawl_page(url: str, site_id: int, crawl_id: int):
    """
    A Celery task to crawl a single page, extract SEO data, and save it to the database.
    """
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
                # TODO: Log the error to the crawl job record
                return {"url": url, "error": f"HTTP status code: {status_code}"}

            html_content = page.content()
            browser.close()

            doc = Document(html_content)
            clean_html = doc.summary()

            full_soup = BeautifulSoup(html_content, 'html.parser')
            seo_data = extract_seo_data(full_soup, url)

            page_data = {
                "status_code": status_code,
                "clean_html": clean_html,
            }

            # Save the extracted data to the database
            crud.create_page_with_elements(db=db, page_data=page_data, seo_data=seo_data, site_id=site_id)

            return {
                "status": "success",
                "url": url,
                "message": "Page crawled and data saved successfully.",
            }

    except PlaywrightTimeoutError:
        # TODO: Log the error to the crawl job record
        return {"url": url, "error": "Navigation timed out."}
    except Exception as e:
        # TODO: Log the error to the crawl job record
        return {"url": url, "error": f"An unexpected error occurred: {str(e)}"}
    finally:
        db.close()

@celery_app.task
def add(x, y):
    """A simple task to test the Celery setup."""
    return x + y
