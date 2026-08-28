import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response, status, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from aiogram.types import Update

from app.core.config import settings
from app.bot.loader import bot, dp
from app.bot.handlers import router as bot_router
from app.api.v1.router import api_router
# در صورت استفاده از SQLAlchemy/Tortoise برای ساخت اولیه جداول یا بررسی اتصال:
# from app.core.database import init_db, close_db

# --- پیکربندی لاگ‌گذاری استاندارد ---
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("product_hub.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    مدیریت چرخه حیات اپلیکیشن (Startup و Shutdown):
    - ثبت روترهای بات
    - بررسی اتصال دیتابیس
    - تنظیم یا حذف Webhook تلگرام
    """
    logger.info("🚀 در حال راه‌اندازی سرویس Product Hub...")
    
    # ۱. ثبت روتر بات در دیسپچر
    dp.include_router(bot_router)

    # ۲. آماده‌سازی دیتابیس (اختیاری در صورت وجود اسکریپت مایگریشن)
    # await init_db()

    # ۳. پیکربندی Webhook تلگرام در صورت فعال بودن در تنظیمات
    if settings.USE_WEBHOOK and settings.WEBHOOK_URL:
        webhook_endpoint = f"{settings.WEBHOOK_URL.rstrip('/')}{settings.BOT_WEBHOOK_PATH}"
        logger.info(f"🔗 در حال تنظیم وب‌هوک تلگرام روی: {webhook_endpoint}")
        
        await bot.set_webhook(
            url=webhook_endpoint,
            secret_token=settings.TELEGRAM_SECRET_TOKEN,
            drop_pending_updates=True,
            allowed_updates=dp.resolve_used_update_types()
        )
    else:
        logger.warning("⚠️ بات در حالت Webhook تنظیم نشده است (مناسب برای توسعه لوکال با runner.py).")

    yield  # نقطه کارکرد فعال سرور

    # --- فرآیند خاموش شدن امن (Graceful Shutdown) ---
    logger.info("🛑 در حال خاموش‌سازی سرویس...")
    
    if settings.USE_WEBHOOK:
        try:
            logger.info("🗑 در حال حذف وب‌هوک تلگرام...")
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception as e:
            logger.error(f"خطا در حذف وب‌هوک: {e}")

    # بستن نشست ارتباطی بات تلگرام
    await bot.session.close()
    
    # بستن ارتباطات دیتابیس در صورت نیاز
    # await close_db()
    logger.info("✅ سرویس با موفقیت متوقف شد.")


# --- ایجاد نمونه FastAPI ---
app = FastAPI(
    title="Product Hub API & Services",
    description="سیستم یکپارچه مدیریت محصولات، صدور بارکد، کاتالوگ Excel/PDF و ربات تلگرام / TMA",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# --- تنظیمات CORS برای دسترسی TMA و پنل وب مستقل ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,  # مثال: ["*"] یا دامنه‌های فرانت‌اند
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- هندلر دریافت آپدیت‌های تلگرام (Webhook) ---
@app.post(
    settings.BOT_WEBHOOK_PATH,
    include_in_schema=False,
    status_code=status.HTTP_200_OK
)
async def telegram_webhook_handler(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None)
) -> Response:
    """
    دریافت ایمن آپدیت‌های وب‌هوک تلگرام و اعتبارسنجی Secret Token
    """
    # اعتبارسنجی امنیتی توکن هدر وب‌هوک
    if settings.TELEGRAM_SECRET_TOKEN:
        if x_telegram_bot_api_secret_token != settings.TELEGRAM_SECRET_TOKEN:
            logger.warning("⛔ درخواست وب‌هوک با Secret Token نامعتبر رد شد.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Invalid secret token"
            )

    try:
        raw_update = await request.json()
        update = Update.model_validate(raw_update, context={"bot": bot})
        await dp.feed_webhook_update(bot=bot, update=update)
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ خطا در پردازش آپدیت تلگرام: {e}", exc_info=True)
        # تلگرام در صورت دریافت هر کدی غیر از 200 مجدداً آپدیت را ارسال می‌کند؛
        # برای جلوگیری از تکرار لوپ خطا، وضعیت 200 برگردانده شده و خطا لاگ می‌شود.
        return Response(status_code=status.HTTP_200_OK)


# --- روت‌های عمومی و Health Check ---
@app.get("/health", tags=["System"])
async def health_check():
    """بررسی وضعیت سلامت سرویس و ارتباطات"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "webhook_enabled": settings.USE_WEBHOOK
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Product Hub API is running.",
        "docs": "/docs" if settings.DEBUG else "Disabled in production"
    }


# --- ثبت روت‌های API (شامل احراز هویت TMA، محصولات و گزارشات) ---
app.include_router(api_router, prefix="/api/v1")


# --- مدیریت خطاهای سراسری (Global Exception Handlers) ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "خطای داخلی سرور رخ داده است. لطفاً با پشتیبانی تماس بگیرید."}
    )