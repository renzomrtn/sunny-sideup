from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:80", "http://localhost:5173"]

    # ── Database ──────────────────────────────────────
    CMS_DB_URL: str = "postgresql+asyncpg://postgres:YouthOutH@db:5432/cms_db"

    # ── RabbitMQ ──────────────────────────────────────
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    # ── Identity Service (for cross-service auth) ─────
    IDENTITY_SERVICE_URL: str = "http://identity-service:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
