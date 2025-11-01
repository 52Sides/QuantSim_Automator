from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    redis_url: str
    kafka_broker: str
    app_env: str = "dev"

    class Config:
        env_file = ".env"


settings = Settings()
