from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduPress API"
    app_env: str = "development"
    client_origin: str = "http://localhost:5173"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/edupress"
    jwt_secret: str = "change-me-in-production"
    jwt_expires_minutes: int = 1440
    
    # Event Bus & Read DB
    redis_url: str = "redis://localhost:6379"
    kafka_url: str = "localhost:9092"
    mongo_url: str = "mongodb://admin:adminpassword@localhost:27017"
    
    # Serverless GPU URLs
    modal_whisper_url: str = "https://tronghieudo2k4--edupress-whisper-inference-api-transcribe.modal.run"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
