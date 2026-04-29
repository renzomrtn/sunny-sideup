"""
Project Service
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.rabbitmq import rabbitmq

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq.startup()
    logger.info("project-service started")
    yield
    await rabbitmq.shutdown()
    logger.info("project-service stopped")


app = FastAPI(
    title="YOUTH Project Service",
    description="Project management and monitoring for SK officials",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.domains.project.router import router as project_router
app.include_router(project_router, prefix="/api/projects", tags=["Projects"])


@app.get("/api/health")
async def health_check():
    return {
        "status":   "ok",
        "service":  "project-service",
        "rabbitmq": "connected" if rabbitmq.is_ready else "disconnected",
    }
