from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import init_db
from .routers import organizations, sites, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Actions to perform on application startup
    init_db()
    yield
    # Actions to perform on application shutdown (none for now)

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(sites.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the SEO Platform API"}
