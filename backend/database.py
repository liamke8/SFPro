import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path

# Build the path to the .env file (backend/.env)
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Load the database URL from environment variables.
# A default value is provided for local development, expecting a PostgreSQL service.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/seo_platform")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency to get a database session for a single request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initializes the database by creating all tables defined in models.py.
    This should be called from a startup script or management command.
    """
    from . import models
    models.Base.metadata.create_all(bind=engine)
