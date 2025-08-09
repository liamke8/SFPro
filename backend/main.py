from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import init_db
from .routers import organizations, sites, auth, crawls

@asynccontextmanager
async def lifespan(app: FastAPI):
    # In a real application, you might have connection pools or other resources
    # to initialize here. For now, we don't need to do anything on startup
    # as the database schema is managed separately (e.g., by Alembic or in tests).
    yield
    # Actions to perform on application shutdown

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(sites.router)
app.include_router(crawls.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the SEO Platform API"}
