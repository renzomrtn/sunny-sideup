from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────
    EVENTING_DB_URL: str = "postgresql+asyncpg://postgres:YouthOutH@db:5432/eventing_db"

    # ── RabbitMQ ──────────────────────────────────────
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
