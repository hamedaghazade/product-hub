import asyncio
import logging
import sys

from app.bot.loader import bot, dp
from app.bot.handlers import router as bot_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

async def main() -> None:
    dp.include_router(bot_router)
    logger.info("Starting Telegram Bot in Polling mode...")
    
    # حذف وب‌هوک‌های قبلی در صورت وجود
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())