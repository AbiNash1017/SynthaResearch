import warnings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")

from config.settings import CORS_ORIGINS
from db.connection import init_db, close_db
from auth.router import router as auth_router
from routers import (
    system_router,
    experiments_router,
    personas_router,
    surveys_router,
    interviews_router,
    reports_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes MongoDB and Beanie on startup, closes connection on shutdown."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Universal Synthetic User Research Platform API",
    description="Backend services for OpenRouter LLM-powered synthetic user research simulations across any product domain.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS Configuration with explicit allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication & Modular Feature Routers
app.include_router(auth_router)
app.include_router(system_router)
app.include_router(experiments_router)
app.include_router(personas_router)
app.include_router(surveys_router)
app.include_router(interviews_router)
app.include_router(reports_router)
