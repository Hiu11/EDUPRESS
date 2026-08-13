from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduPress API"
    app_env: str = "development"
    log_level: str = "INFO"
    log_format: str = "json"
    client_origin: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://postgres:postgrespassword@localhost:5432/edupress_write"
    jwt_secret: str = "change-me-in-production"
    jwt_expires_minutes: int = 1440
    
    # Event Bus & Read DB
    redis_url: str = "redis://localhost:6379"
    kafka_url: str = "localhost:9092"
    mongo_url: str = "mongodb://admin:adminpassword@localhost:27017/?authSource=admin"
    
    # Serverless GPU URLs
    modal_whisper_url: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def sync_database_url(self) -> str:
        # SQLAlchemy 2.0 requires postgresql:// instead of postgres://
        # and since we use psycopg3, we should enforce postgresql+psycopg://
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

settings = Settings()
