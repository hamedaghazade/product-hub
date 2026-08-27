import asyncio
import logging
from app.bot.loader import bot, dp
from app.bot.handlers import bot_router
from app.core.database import engine, Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("product_hub.bot_runner")

async def main():
    logger.info("در حال آماده‌سازی پایگاه داده...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    dp.include_router(bot_router)

    # پاک‌سازی وب‌هوک قبلی جهت شروع دریافت پیام‌ها به صورت Polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("بات با موفقیت به حالت Polling متصل شد. آماده دریافت پیام...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())