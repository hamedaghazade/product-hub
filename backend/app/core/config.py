from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_SECRET_TOKEN: str = "super-secret-hex-token"
    USE_WEBHOOK: bool = False
    WEBHOOK_URL: str = "https://your-domain.com"
    BOT_WEBHOOK_PATH: str = "/api/v1/bot/webhook"
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()