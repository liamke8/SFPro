import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Schemas for Sites
class SiteBase(BaseModel):
    domain: str
    robots_policy: Optional[str] = 'respect'

class SiteCreate(SiteBase):
    pass

class Site(SiteBase):
    id: int
    org_id: int

    model_config = ConfigDict(from_attributes=True)

# Schemas for Users
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    org_id: int
    role: str

class User(UserBase):
    id: int
    org_id: int
    role: str

    model_config = ConfigDict(from_attributes=True)

# Schemas for Organizations
class OrganizationBase(BaseModel):
    name: str
    plan: Optional[str] = 'free'

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    credits_balance: int
    sites: List[Site] = []

    model_config = ConfigDict(from_attributes=True)

# Schemas for Crawls
class CrawlBase(BaseModel):
    site_id: int

class CrawlCreate(CrawlBase):
    urls: List[str]

class Crawl(CrawlBase):
    id: int
    status: str
    started_at: Optional[datetime.datetime] = None
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
