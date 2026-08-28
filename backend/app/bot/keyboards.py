from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    WebAppInfo
)

def get_main_menu_keyboard(web_app_url: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ ثبت محصول جدید"),
                KeyboardButton(text="📱 باز کردن مینی‌اپ", web_app=WebAppInfo(url=web_app_url))
            ],
            [
                KeyboardButton(text="📊 دریافت خروجی اکسل"),
                KeyboardButton(text="📄 دریافت کاتالوگ PDF")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌های زیر را انتخاب کنید..."
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ انصراف")]],
        resize_keyboard=True
    )

def get_confirm_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ تایید و ذخیره", callback_data="confirm_product"),
                InlineKeyboardButton(text="❌ لغو", callback_data="cancel_product")
            ]
        ]
    )