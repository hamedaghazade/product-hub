import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from app.bot.states import ProductRegistrationFSM
from app.bot.keyboards import (
    get_main_menu_keyboard, 
    get_cancel_keyboard, 
    get_confirm_inline_keyboard
)
from app.bot.validators import (
    normalize_digits, 
    validate_and_normalize_barcode, 
    parse_price, 
    parse_int_positive
)
from app.services.barcode_service import BarcodeService
from app.services.excel_service import ExcelExportService
from app.services.pdf_service import PDFExportService
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)
router = Router(name="bot_handlers")

WEB_APP_URL = "https://your-domain.com/tma"


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 **به سامانه یکپارچه مدیریت محصولات خوش آمدید.**\n\n"
        "برای ثبت کالا، دریافت کاتالوگ Excel/PDF یا ورود به Mini App از گزینه‌های زیر استفاده کنید:",
        reply_markup=get_main_menu_keyboard(WEB_APP_URL),
        parse_mode="Markdown"
    )


@router.message(F.text == "❌ انصراف")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("عملیاتی در حال انجام نیست.", reply_markup=get_main_menu_keyboard(WEB_APP_URL))
        return
    await state.clear()
    await message.answer("❌ فرآیند جاری لغو شد.", reply_markup=get_main_menu_keyboard(WEB_APP_URL))


# --- مراحل ثبت کالا (FSM) ---

@router.message(F.text == "➕ ثبت محصول جدید")
async def start_product_registration(message: Message, state: FSMContext):
    await state.set_state(ProductRegistrationFSM.title)
    await message.answer(
        "📌 **مرحله ۱:** لطفاً **نام کالا** را وارد کنید:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )


@router.message(ProductRegistrationFSM.title)
async def process_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if len(title) < 2:
        await message.answer("⚠️ نام کالا باید حداقل ۲ کاراکتر باشد. دوباره وارد کنید:")
        return
    await state.update_data(title=title)
    await state.set_state(ProductRegistrationFSM.cost_price)
    await message.answer("💰 **مرحله ۲:** لطفاً **قیمت خرید/پایه** (به تومان) را وارد کنید:", parse_mode="Markdown")


@router.message(ProductRegistrationFSM.cost_price)
async def process_cost_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("⚠️ قیمت نامعتبر است. لطفاً عدد وارد کنید:")
        return
    await state.update_data(cost_price=price)
    await state.set_state(ProductRegistrationFSM.units_per_pack)
    await message.answer("📦 **مرحله ۳:** لطفاً **تعداد در بسته** را وارد کنید:", parse_mode="Markdown")


@router.message(ProductRegistrationFSM.units_per_pack)
async def process_units_per_pack(message: Message, state: FSMContext):
    units = parse_int_positive(message.text)
    if units is None:
        await message.answer("⚠️ تعداد باید یک عدد صحیح بزرگ‌تر از صفر باشد:")
        return
    await state.update_data(units_per_pack=units)
    await state.set_state(ProductRegistrationFSM.barcode_value)
    await message.answer("🏷 **مرحله ۴:** لطفاً **کد بارکد** کالا را وارد کنید:", parse_mode="Markdown")


@router.message(ProductRegistrationFSM.barcode_value)
async def process_barcode(message: Message, state: FSMContext):
    is_valid, barcode_val = validate_and_normalize_barcode(message.text)
    if not is_valid:
        await message.answer("⚠️ بارکد وارد شده نامعتبر است. لطفاً کد بارکد را ارسال کنید:")
        return
    await state.update_data(barcode_value=barcode_val)
    await state.set_state(ProductRegistrationFSM.consumer_price)
    await message.answer("🏷 **مرحله ۵:** لطفاً **قیمت مصرف‌کننده** (به تومان) را وارد کنید:", parse_mode="Markdown")


@router.message(ProductRegistrationFSM.consumer_price)
async def process_consumer_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("⚠️ قیمت مصرف‌کننده نامعتبر است. لطفاً عدد وارد کنید:")
        return
    await state.update_data(consumer_price=price)
    data = await state.get_data()

    summary = (
        "📋 **پیش‌نمایش اطلاعات محصول:**\n\n"
        f"🔹 **نام کالا:** {data['title']}\n"
        f"🔹 **قیمت خرید:** {data['cost_price']:,.0f} تومان\n"
        f"🔹 **تعداد در بسته:** {data['units_per_pack']}\n"
        f"🔹 **بارکد:** `{data['barcode_value']}`\n"
        f"🔹 **قیمت مصرف‌کننده:** {data['consumer_price']:,.0f} تومان\n\n"
        "آیا این اطلاعات مورد تایید است؟"
    )
    await state.set_state(ProductRegistrationFSM.confirm)
    await message.answer(summary, reply_markup=get_confirm_inline_keyboard(), parse_mode="Markdown")


@router.callback_query(ProductRegistrationFSM.confirm, F.data == "confirm_product")
async def confirm_product_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # ذخیره در سرویس محصولات
    await ProductService.create_product(data)
    await state.clear()
    await callback.message.edit_text("✅ محصول با موفقیت در دیتابیس ثبت شد.")
    await callback.message.answer("عملیات بعدی را انتخاب کنید:", reply_markup=get_main_menu_keyboard(WEB_APP_URL))
    await callback.answer()


@router.callback_query(ProductRegistrationFSM.confirm, F.data == "cancel_product")
async def cancel_product_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ فرآیند ثبت لغو گردید.")
    await callback.message.answer("بازگشت به منوی اصلی:", reply_markup=get_main_menu_keyboard(WEB_APP_URL))
    await callback.answer()


# --- خروجی اکسل واقعی با بارکدهای درون حافظه ---

@router.message(F.text == "📊 دریافت خروجی اکسل")
async def export_excel_handler(message: Message):
    wait_msg = await message.answer("⏳ در حال تولید فایل اکسل به همراه بارکدهای تعبیه شده...")
    try:
        products = await ProductService.get_all_products()
        if not products:
            await message.answer("⚠️ هنوز هیچ محصولی در سیستم ثبت نشده است.")
            return

        excel_stream = ExcelExportService.generate_product_catalog(products)
        file_bytes = excel_stream.getvalue()

        file = BufferedInputFile(file_bytes, filename="products_catalog.xlsx")
        await message.answer_document(document=file, caption=f"📊 کاتالوگ اکسل با {len(products)} محصول خدمت شما.")
    except Exception as e:
        logger.error(f"Error generating Excel: {e}", exc_info=True)
        await message.answer("⚠️ خطایی در تولید فایل اکسل رخ داد.")
    finally:
        await wait_msg.delete()


# --- خروجی PDF واقعی با چیدمان RTL و بارکد ---

@router.message(F.text == "📄 دریافت کاتالوگ PDF")
async def export_pdf_handler(message: Message):
    wait_msg = await message.answer("⏳ در حال رندر و ساخت فایل PDF کاتالوگ...")
    try:
        products = await ProductService.get_all_products()
        if not products:
            await message.answer("⚠️ هنوز هیچ محصولی در سیستم ثبت نشده است.")
            return

        pdf_stream = PDFExportService.generate_pdf_catalog(products)
        file_bytes = pdf_stream.getvalue()

        file = BufferedInputFile(file_bytes, filename="products_catalog.pdf")
        await message.answer_document(document=file, caption=f"📄 کاتالوگ PDF آماده چاپ با {len(products)} محصول خدمت شما.")
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        await message.answer("⚠️ خطایی در تولید فایل PDF رخ داد.")
    finally:
        await wait_msg.delete()