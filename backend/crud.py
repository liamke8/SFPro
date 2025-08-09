import json
from sqlalchemy.orm import Session, joinedload
from . import models, schemas

# CRUD for Organizations
def get_organization(db: Session, org_id: int):
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization).offset(skip).limit(limit).all()

def create_organization(db: Session, org: schemas.OrganizationCreate):
    db_org = models.Organization(name=org.name, plan=org.plan)
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

# CRUD for Users
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, name=user.name, org_id=user.org_id, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# CRUD for Sites
def get_site(db: Session, site_id: int):
    return db.query(models.Site).filter(models.Site.id == site_id).first()

def create_page_with_elements(db: Session, page_data: dict, seo_data: dict, site_id: int):
    """
    Creates a Page and its associated PageElement record from crawled data.
    """
    page = models.Page(
        site_id=site_id,
        url=seo_data.get("url"),
        status_code=page_data.get("status_code"),
        canonical=seo_data.get("canonical_url"),
        meta_robots=seo_data.get("meta_robots"),
        # word_count will be calculated later
    )
    db.add(page)
    db.commit()
    db.refresh(page)

    page_element = models.PageElement(
        page_id=page.id,
        title=seo_data.get("title"),
        description=seo_data.get("meta_description"),
        h1=seo_data.get("h1"),
        h2_json=json.dumps(seo_data.get("h2s")),
        og_json=json.dumps(seo_data.get("og_tags")),
        schema_json=json.dumps(seo_data.get("schema_ld_json")),
        links_json=json.dumps(seo_data.get("links")),
        images_json=json.dumps(seo_data.get("images")),
    )
    db.add(page_element)
    db.commit()
    db.refresh(page_element)

    return page

def get_sites_by_organization(db: Session, org_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Site).filter(models.Site.org_id == org_id).offset(skip).limit(limit).all()

def create_site_for_organization(db: Session, site: schemas.SiteCreate, org_id: int):
    db_site = models.Site(**site.model_dump(), org_id=org_id)
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site

# CRUD for Crawls
def create_crawl_job(db: Session, site_id: int, total_urls: int):
    """
    Creates a new Crawl job record.
    """
    crawl = models.Crawl(
        site_id=site_id,
        status="starting",
        total_pages=total_urls,
    )
    db.add(crawl)
    db.commit()
    db.refresh(crawl)
    return crawl

def get_pages_by_site(db: Session, site_id: int, skip: int = 0, limit: int = 100):
    """
    Gets all pages for a given site with pagination.
    Eagerly loads page_elements.
    """
    query = db.query(models.Page).filter(models.Page.site_id == site_id).options(joinedload(models.Page.page_elements))
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}
