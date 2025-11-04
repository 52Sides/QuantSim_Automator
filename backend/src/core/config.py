from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/quantsim_db"
    REDIS_URL: str = "redis://redis:6379/0"

    KAFKA_BROKER: str = "kafka:9092"
    KAFKA_SIMULATION_TOPIC: str = "simulation-requests"
    REDIS_PUBSUB_CHANNEL: str = "sim_progress"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    app_env: str = "dev"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
