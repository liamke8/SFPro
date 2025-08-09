import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship, declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Organization(Base):
    __tablename__ = "orgs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    plan = Column(String)
    credits_balance = Column(Integer, default=0)
    users = relationship("User", back_populates="organization")
    sites = relationship("Site", back_populates="organization")
    templates = relationship("Template", back_populates="organization")
    credits_ledger_entries = relationship("CreditsLedger", back_populates="organization")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    org_id = Column(Integer, ForeignKey("orgs.id"))
    role = Column(String)  # e.g., 'owner', 'admin', 'editor'
    organization = relationship("Organization", back_populates="users")
    prompt_runs = relationship("PromptRun", back_populates="user")


class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"))
    domain = Column(String, index=True)
    robots_policy = Column(String, default="respect")
    organization = relationship("Organization", back_populates="sites")
    crawls = relationship("Crawl", back_populates="site")
    pages = relationship("Page", back_populates="site")
    publish_jobs = relationship("PublishJob", back_populates="site")
    wp_integration = relationship("WordpressIntegration", back_populates="site")


class Crawl(Base):
    __tablename__ = "crawls"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    mode = Column(Enum("full", "csv", name="crawl_mode_enum"), default="full")
    total_pages = Column(Integer, default=0)
    status = Column(String, default="pending")  # e.g., pending, running, completed, failed
    site = relationship("Site", back_populates="crawls")


class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    url = Column(String, index=True)
    status_code = Column(Integer)
    canonical = Column(String)
    meta_robots = Column(String)
    content_html = Column(Text)
    content_md = Column(Text)
    word_count = Column(Integer)
    last_crawled_at = Column(DateTime, default=datetime.datetime.utcnow)
    site = relationship("Site", back_populates="pages")
    page_elements = relationship("PageElement", back_populates="page", uselist=False)
    embeddings = relationship("Embedding", back_populates="page")
    row_generations = relationship("RowGeneration", back_populates="page")
    publish_jobs = relationship("PublishJob", back_populates="page")


class PageElement(Base):
    __tablename__ = "page_elements"
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"), unique=True)
    title = Column(String)
    description = Column(String)
    h1 = Column(String)
    h2_json = Column(JSON)
    og_json = Column(JSON)
    schema_json = Column(JSON)
    links_json = Column(JSON)
    images_json = Column(JSON)
    page = relationship("Page", back_populates="page_elements")


class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"))
    kind = Column(String)  # e.g., 'page', 'title', 'h1', 'chunk'
    vector = Column(Vector(384))  # Example dimension for bge-m3
    page = relationship("Page", back_populates="embeddings")


class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"))
    name = Column(String)
    system_prompt = Column(Text)
    user_prompt = Column(Text)
    output_schema = Column(JSON)
    model = Column(String)
    vars_json = Column(JSON)
    version = Column(Integer, default=1)
    organization = relationship("Organization", back_populates="templates")
    prompt_runs = relationship("PromptRun", back_populates="template")


class PromptRun(Base):
    __tablename__ = "prompt_runs"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String)  # e.g., 'running', 'completed'
    template = relationship("Template", back_populates="prompt_runs")
    user = relationship("User", back_populates="prompt_runs")
    row_generations = relationship("RowGeneration", back_populates="prompt_run")
    credits_ledger_entries = relationship("CreditsLedger", back_populates="prompt_run")


class RowGeneration(Base):
    __tablename__ = "row_generations"
    id = Column(Integer, primary_key=True, index=True)
    prompt_run_id = Column(Integer, ForeignKey("prompt_runs.id"))
    page_id = Column(Integer, ForeignKey("pages.id"))
    input_context_json = Column(JSON)
    output_json = Column(JSON)
    tokens_in = Column(Integer)
    tokens_out = Column(Integer)
    variant = Column(Integer, default=1)
    prompt_run = relationship("PromptRun", back_populates="row_generations")
    page = relationship("Page", back_populates="row_generations")


class PublishJob(Base):
    __tablename__ = "publish_jobs"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    page_id = Column(Integer, ForeignKey("pages.id"))
    cms = Column(Enum("wordpress", name="cms_enum"))
    payload_json = Column(JSON)
    status = Column(String)  # 'pending', 'published', 'failed'
    error = Column(Text)
    site = relationship("Site", back_populates="publish_jobs")
    page = relationship("Page", back_populates="publish_jobs")


class WordpressIntegration(Base):
    __tablename__ = "integrations_wp"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    base_url = Column(String)
    api_key = Column(String)
    seo_plugin_detected = Column(String)
    site = relationship("Site", back_populates="wp_integration", uselist=False)


class CreditsLedger(Base):
    __tablename__ = "credits_ledger"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"))
    kind = Column(Enum("crawl", "gen", name="credit_kind_enum"))
    amount = Column(Integer)
    model = Column(String, nullable=True)
    page_count = Column(Integer, nullable=True)
    run_id = Column(Integer, ForeignKey("prompt_runs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    organization = relationship("Organization", back_populates="credits_ledger_entries")
    prompt_run = relationship("PromptRun", back_populates="credits_ledger_entries")
