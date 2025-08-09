import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int

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

# Schemas for Page Elements
class PageElement(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    h1: Optional[str] = None
    h2_json: Optional[dict] = None
    og_json: Optional[dict] = None
    schema_json: Optional[dict] = None
    links_json: Optional[dict] = None
    images_json: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)

# Schemas for Pages
class Page(BaseModel):
    id: int
    url: str
    status_code: Optional[int] = None
    canonical: Optional[str] = None
    meta_robots: Optional[str] = None
    word_count: Optional[int] = None
    last_crawled_at: Optional[datetime.datetime] = None
    page_elements: Optional[PageElement] = None

    model_config = ConfigDict(from_attributes=True)

# Schemas for Templates
class TemplateBase(BaseModel):
    name: str
    system_prompt: Optional[str] = None
    user_prompt: str
    output_schema: Optional[dict] = None
    model: str = "ollama/llama3"
    vars_json: Optional[dict] = None

class TemplateCreate(TemplateBase):
    org_id: int

class Template(TemplateBase):
    id: int
    org_id: int
    version: int

    model_config = ConfigDict(from_attributes=True)

# Schemas for Prompt Runs and Generations
class PromptRunBase(BaseModel):
    template_id: int
    user_id: int

class PromptRunCreate(PromptRunBase):
    pass

class RowGeneration(BaseModel):
    id: int
    output_json: dict
    variant: int

    model_config = ConfigDict(from_attributes=True)

class PromptRun(PromptRunBase):
    id: int
    status: str
    created_at: datetime.datetime
    row_generations: List[RowGeneration] = []

    model_config = ConfigDict(from_attributes=True)

class RunPromptRequest(BaseModel):
    template_id: int
