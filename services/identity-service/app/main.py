import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.rabbitmq import rabbitmq
from app.domains.identity import router_auth, router_accounts, router_tenants, router_roles
from app.services.outbox_relay import run_outbox_relay

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq.startup()
    tasks = [
        asyncio.create_task(run_outbox_relay(), name="outbox-relay"),
    ]
    logger.info("identity-service started — outbox relay running")
    yield
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await rabbitmq.shutdown()
    logger.info("identity-service stopped")


app = FastAPI(
    title="YOUTH Identity Service",
    description="Accounts, authentication, roles, and tenants",
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

app.include_router(router_auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(router_accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(router_tenants.router,  prefix="/api/tenants",  tags=["Tenants"])
app.include_router(router_roles.router,    prefix="/api/roles",    tags=["Roles"])


@app.get("/api/health")
async def health_check():
    return {
        "status":   "ok",
        "service":  "identity-service",
        "rabbitmq": "connected" if rabbitmq.is_ready else "disconnected",
    }
