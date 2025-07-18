from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from logging import Logger
from app.utils import get_logger

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use .env in ./backend/
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    logger: Logger = get_logger('job-app-logger')

    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    MONGO_URI: str


settings = Settings()
