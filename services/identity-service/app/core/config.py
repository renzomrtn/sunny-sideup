from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:80", "http://localhost:5173"]

    # ── Database ──────────────────────────────────────
    IDENTITY_DB_URL: str = "postgresql+asyncpg://postgres:YouthOutH@db:5432/identity_db"

    # ── RabbitMQ ──────────────────────────────────────
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    # ── Authentik OIDC ────────────────────────────────
    AUTHENTIK_URL:           str = "http://authentik-server:9000"
    AUTHENTIK_SLUG:          str = "youth-account-mgmt"
    AUTHENTIK_CLIENT_ID:     str = "youth-account-mgmt-client"
    AUTHENTIK_CLIENT_SECRET: str = ""
    AUTHENTIK_REDIRECT_URI:  str = "http://localhost/auth/callback"

    # ── Authentik Admin API ───────────────────────────
    # Token from: Authentik Admin UI → Directory → Tokens → Create (Intent: API)
    AUTHENTIK_API_TOKEN:      str = ""
    # Temporary password assigned to all auto-created Authentik users on import.
    # Users should change this on first login.
    AUTHENTIK_DEFAULT_PASSWORD: str = "@youthsysteminthebig'26"

    # Seed admin
    SEED_ADMIN_AUTH_ID: str = "18f71d90-5003-4df1-a0b1-ff445e454f30"

    MAINSYS_CLIENT_ID:     str = ""
    MAINSYS_CLIENT_SECRET: str = ""
    MAINSYS_AUTHENTIK_SLUG: str = "youth-mainsys"

    # ── Pagination ────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
