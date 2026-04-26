from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: Optional[str] = None  # For OpenRouter or other providers
    OPENAI_MODEL: str = "gpt-4"  # Default model
    DATABASE_URL: str = "sqlite:///./analytics.db"
    REDIS_URL: Optional[str] = None
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
