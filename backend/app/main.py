from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.health import health_router
from app.api.product_routes import router as product_router
from app.api.export_routes import router as export_router
from app.bot.loader import bot, dp
from app.bot.handlers import bot_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ایجاد جداول دیتابیس در زمان استارت‌آپ
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    dp.include_router(bot_router)
    # در محیط پروداکشن وب‌هوک و در محیط محلی Polling لود می‌شود
    yield
    await bot.session.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(product_router, prefix=settings.API_V1_STR)
app.include_router(export_router, prefix=settings.API_V1_STR)