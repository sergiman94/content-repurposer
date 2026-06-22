from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_whisper_model: str = "whisper-large-v3-turbo"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Storage
    storage_dir: str = "./data"
    max_upload_size_mb: int = 500
    max_audio_duration_minutes: int = 180

    # App
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_prefix": "REPURPOSE_"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
