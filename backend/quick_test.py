import sys
import os

# افزودن مسیر ریشه بک‌اند به sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.barcode_service import BarcodeService, BarcodeConfig, BarcodeFormat, BarcodeEngine
from app.schemas.product import ProductCreate

def run_tests():
    print("--- شروع تست یکپارچگی Backend ---")

    # تست ۱: ایمپورت و ساختار کلاس‌ها
    assert BarcodeService is BarcodeEngine, "BarcodeEngine alias mismatch"
    print("✓ [Pass] نام‌ها و Alias ماژول بارکد تأیید شد.")

    # تست ۲: اعتبارسنجی اسکیما کالا
    product = ProductCreate(
        title="روغن سرخ‌کردنی شفاف ۱.۵ لیتری",
        cost_price=85000,
        units_per_pack=6,
        barcode_value="626012345678",
        consumer_price=110000
    )
    print(f"✓ [Pass] اسکیمای کالا اعتبارسنجی شد: {product.title}")

    # تست ۳: تولید بافر بارکد در حافظه
    config = BarcodeConfig(
        title=product.title,
        code_value=product.barcode_value,
        format_type=BarcodeFormat.EAN13
    )
    buffer = BarcodeService.generate_barcode_image(config)
    size_kb = buffer.getbuffer().nbytes / 1024
    print(f"✓ [Pass] بافر تصویر بارکد EAN-13 با موفقیت ایجاد شد (حجم: {size_kb:.2f} KB)")

    print("\n--- تمامی تست‌ها با موفقیت پاس شدند ---")

if __name__ == "__main__":
    run_tests()