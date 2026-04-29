from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:5173",
        "http://localhost:5174",
    ]
    PROJECT_DB_URL: str = "postgresql+asyncpg://postgres:changeme_postgres@db:5432/project_db"
    RABBITMQ_URL: str = "amqp://guest:changeme_rabbitmq@rabbitmq:5672/"
    IDENTITY_SERVICE_URL: str = "http://identity-service:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
