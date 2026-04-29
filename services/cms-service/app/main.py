"""
Cms Service — Scaffold
─────────────────────
Not yet implemented. Structure is ready — add domain logic and
uncomment the router include below to activate endpoints.
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
    logger.info("cms-service started")
    yield
    await rabbitmq.shutdown()
    logger.info("cms-service stopped")


app = FastAPI(
    title="YOUTH Cms Service",
    description="Cms management",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Uncomment when domain router is ready ─────────────────────────────────
# from app.domains.cms.router import router as cms_router
# app.include_router(cms_router, prefix="/api/cms", tags=["Cms"])


@app.get("/api/health")
async def health_check():
    return {
        "status":   "ok",
        "service":  "cms-service",
        "rabbitmq": "connected" if rabbitmq.is_ready else "disconnected",
    }
