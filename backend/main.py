from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from .database import init_db
from .routers import organizations, sites, auth, crawls, templates, prompts, users, chat, export, publish

@asynccontextmanager
async def lifespan(app: FastAPI):
    # In a real application, you might have connection pools or other resources
    # to initialize here. For now, we don't need to do anything on startup
    # as the database schema is managed separately (e.g., by Alembic or in tests).
    yield
    # Actions to perform on application shutdown

app = FastAPI(lifespan=lifespan)

# Add a prefix to all API routes
api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(sites.router)
api_router.include_router(crawls.router)
api_router.include_router(templates.router)
api_router.include_router(prompts.router)
api_router.include_router(users.router)
api_router.include_router(chat.router)
api_router.include_router(export.router)
api_router.include_router(publish.router)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the SEO Platform API"}
