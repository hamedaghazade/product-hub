from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Product Hub"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change-in-production"
    BOT_TOKEN: str = ""
    WEBHOOK_URL: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./products.db"
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()\n