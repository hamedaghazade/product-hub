from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from sqlalchemy import select

from app.bot.loader import bot
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.product import Product
from app.services.excel_service import ExcelExportService
from app.services.pdf_service import PDFExportService

bot_router = Router()

def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 باز کردن پنل مدیریت (Mini App)", 
                web_app=WebAppInfo(url=settings.WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(text="📊 دانلود کاتالوگ Excel", callback_data="bot_export_excel"),
            InlineKeyboardButton(text="📄 دانلود کاتالوگ PDF", callback_data="bot_export_pdf")
        ]
    ])

@bot_router.message(CommandStart())
async def handle_start(message: types.Message):
    welcome_text = (
        f"سلام <b>{message.from_user.first_name}</b> عزیز 👋\n\n"
        "به سامانه یکپارچه مدیریت کالا و بارکد <b>Product Hub</b> خوش آمدید.\n"
        "برای ثبت محصول جدید، مدیریت انبار و مشاهده پیش‌نمایش بارکدها دکمه زیر را لمس کنید:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@bot_router.callback_query(F.data == "bot_export_excel")
async def cb_export_excel(callback: types.CallbackQuery):
    await callback.answer("⏳ در حال پردازش و تولید فایل اکسل...")
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Product).order_by(Product.id))
        products = res.scalars().all()

    if not products:
        await callback.message.answer("⚠️ هنوز هیچ کالایی در سامانه ثبت نشده است.")
        return

    excel_stream = ExcelExportService.generate_products_workbook(products)
    file_bytes = excel_stream.getvalue()

    await callback.message.answer_document(
        document=BufferedInputFile(file_bytes, filename="Products_Catalog.xlsx"),
        caption="📋 <b>فایل اکسل کاتالوگ محصولات</b> به همراه بارکدهای Embed شده درون سلول‌ها."
    )

@bot_router.callback_query(F.data == "bot_export_pdf")
async def cb_export_pdf(callback: types.CallbackQuery):
    await callback.answer("⏳ در حال تولید سند PDF چاپی...")
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Product).order_by(Product.id))
        products = res.scalars().all()

    if not products:
        await callback.message.answer("⚠️ هنوز هیچ کالایی در سامانه ثبت نشده است.")
        return

    pdf_stream = PDFExportService.generate_products_pdf(products)
    file_bytes = pdf_stream.getvalue()

    await callback.message.answer_document(
        document=BufferedInputFile(file_bytes, filename="Products_Catalog.pdf"),
        caption="📄 <b>کاتالوگ چاپی محصولات (PDF)</b> با پشتیبانی کامل از چینش فارسی و بارکد."
    )