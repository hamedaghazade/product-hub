from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Product Hub API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # دیتابیس (پیش‌فرض SQLite برای محیط لوکال و تست؛ قابل سوئیچ به PostgreSQL)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./product_hub.db",
        description="Async Database Connection String"
    )
    
    # تنظیمات امنیتی و تلگرام
    BOT_TOKEN: str = Field(default="YOUR_TELEGRAM_BOT_TOKEN_HERE")
    WEBAPP_URL: str = Field(default="https://yourdomain.com")
    WEBHOOK_SECRET: str = Field(default="super-secret-webhook-key")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()