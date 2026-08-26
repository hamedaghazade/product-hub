from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from app.core.config import settings
from app.api.endpoints import DATABASE_MEMORY
from app.services.excel_service import ExcelService
from app.services.pdf_service import PDFService

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    webapp_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 باز کردن پنل مدیریت (TMA)", web_app=WebAppInfo(url=settings.CORS_ORIGINS[0]))],
        [InlineKeyboardButton(text="📊 دریافت اکسل", callback_data="export_excel"),
         InlineKeyboardButton(text="📄 دریافت PDF", callback_data="export_pdf")]
    ])
    await message.answer(
        "سلام! به سیستم مدیریت یکپارچه محصولات خوش آمدید.\n"
        "جهت ثبت و مدیریت سریع محصولات از دکمه زیر استفاده فرمایید:",
        reply_markup=webapp_btn
    )

@dp.callback_query(F.data == "export_excel")
async def process_export_excel(callback: types.CallbackQuery, bot: Bot):
    if not DATABASE_MEMORY:
        await callback.answer("هیچ محصولی ثبت نشده است.", show_alert=True)
        return
    await callback.answer("در حال ساخت فایل اکسل...")
    stream = ExcelService.generate_products_sheet(DATABASE_MEMORY)
    file = BufferedInputFile(stream.getvalue(), filename="products.xlsx")
    await bot.send_document(chat_id=callback.message.chat.id, document=file)

@dp.callback_query(F.data == "export_pdf")
async def process_export_pdf(callback: types.CallbackQuery, bot: Bot):
    if not DATABASE_MEMORY:
        await callback.answer("هیچ محصولی ثبت نشده است.", show_alert=True)
        return
    await callback.answer("در حال آماده‌سازی PDF...")
    stream = PDFService.generate_products_pdf(DATABASE_MEMORY)
    file = BufferedInputFile(stream.getvalue(), filename="products.pdf")
    await bot.send_document(chat_id=callback.message.chat.id, document=file)\n