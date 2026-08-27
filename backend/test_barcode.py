import sys
import os

# اضافه کردن روت بک‌اند به sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.barcode_service import BarcodeService, BarcodeConfig, BarcodeFormat

def run_test():
    print("در حال تست تولید تصویر بارکد...")
    try:
        config = BarcodeConfig(
            title="روغن سرخ‌کردنی شفاف ۱.۵ لیتری",
            code_value="626012345678", # ۱۲ رقم (رقم ۱۳ام خودکار محاسبه خواهد شد)
            format_type=BarcodeFormat.EAN13,
            title_font_size=24,
            code_font_size=20,
            barcode_height_px=140
        )
        
        img_buffer = BarcodeService.generate_barcode_image(config)
        
        output_filename = "test_barcode_output.png"
        with open(output_filename, "wb") as f:
            f.write(img_buffer.getvalue())
            
        print(f" تصویر با موفقیت تولید شد: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f" خطا در تست بارکد: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()