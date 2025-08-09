from sqlalchemy.orm import Session
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

def get_sites_by_organization(db: Session, org_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Site).filter(models.Site.org_id == org_id).offset(skip).limit(limit).all()

def create_site_for_organization(db: Session, site: schemas.SiteCreate, org_id: int):
    db_site = models.Site(**site.model_dump(), org_id=org_id)
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site
