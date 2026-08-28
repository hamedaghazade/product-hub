import os
from io import BytesIO
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import arabic_reshaper
from bidi.algorithm import get_display

# پیکربندی اختصاصی برای پشتیبانی کامل از حروف فارسی (گ، چ، پ، ژ و تنوین‌ها)
_RESHAPER_CONFIG = {
    'delete_harakat': False,
    'support_ligatures': True,
    'shift_harakat_position': False,
    'use_unshaped_instead_of_isolated': True
}
_reshaper = arabic_reshaper.ArabicReshaper(configuration=_RESHAPER_CONFIG)

def get_persian_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """جستجوی مسیر فونت فارسی معتبر با چندین Fallback مطمئن"""
    font_paths = [
        os.getenv("PERSIAN_FONT_BOLD_PATH", "assets/fonts/Vazirmatn-Bold.ttf"),
        os.getenv("PERSIAN_FONT_PATH", "assets/fonts/Vazirmatn-Regular.ttf"),
        "backend/assets/fonts/Vazirmatn-Bold.ttf",
        "backend/assets/fonts/Vazirmatn-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

class BarcodeService:
    @staticmethod
    def reshape_persian(text: str) -> str:
        """اصلاح ترتیب حروف و اتصال کاراکترهای فارسی"""
        if not text:
            return ""
        reshaped = _reshaper.reshape(str(text).strip())
        return get_display(reshaped)

    @classmethod
    def generate_barcode_image(
        cls,
        title: str,
        barcode_value: str,
        width_scale: float = 1.0,
        height_scale: float = 1.0
    ) -> BytesIO:
        clean_value = str(barcode_value).strip()

        # انتخاب نوع بارکد بر اساس مقدار ورودی
        if clean_value.isdigit() and len(clean_value) == 13:
            barcode_class = barcode.get_barcode_class('ean13')
        else:
            barcode_class = barcode.get_barcode_class('code128')

        writer = ImageWriter()
        writer.set_options({
            'write_text': False,
            'module_width': 0.28 * width_scale,
            'module_height': 14.0 * height_scale,
            'quiet_zone': 2.5,
        })

        raw_buffer = BytesIO()
        barcode_instance = barcode_class(clean_value, writer=writer)
        barcode_instance.write(raw_buffer)
        raw_buffer.seek(0)

        barcode_img = Image.open(raw_buffer).convert("RGBA")
        bw, bh = barcode_img.size

        # ابعاد فونت بزرگتر و خواناتر
        title_font = get_persian_font(size=19)
        code_font = get_persian_font(size=14)

        reshaped_title = cls.reshape_persian(title)

        # ساخت بوم موقت برای محاسبه دقیق ابعاد متن
        temp_img = Image.new("RGBA", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        t_bbox = temp_draw.textbbox((0, 0), reshaped_title, font=title_font)
        title_w = t_bbox[2] - t_bbox[0]
        title_h = t_bbox[3] - t_bbox[1]

        c_bbox = temp_draw.textbbox((0, 0), clean_value, font=code_font)
        code_w = c_bbox[2] - c_bbox[0]
        code_h = c_bbox[3] - c_bbox[1]

        # تعیین ابعاد Canvas با در نظر گرفتن حاشیه‌های بالا و پایین
        padding_x = 24
        canvas_width = max(bw + padding_x, title_w + padding_x, 260)
        canvas_height = bh + title_h + code_h + 35

        canvas = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        # ۱. رسم عنوان کالا در بالا
        title_x = (canvas_width - title_w) // 2
        title_y = 10
        draw.text((title_x, title_y), reshaped_title, fill=(15, 23, 42, 255), font=title_font)

        # ۲. قرار دادن خطوط بارکد در مرکز
        barcode_x = (canvas_width - bw) // 2
        barcode_y = title_y + title_h + 10
        canvas.paste(barcode_img, (barcode_x, barcode_y), barcode_img)

        # ۳. رسم کد بارکد در زیر خطوط
        code_x = (canvas_width - code_w) // 2
        code_y = barcode_y + bh + 4
        draw.text((code_x, code_y), clean_value, fill=(51, 65, 85, 255), font=code_font)

        output_stream = BytesIO()
        canvas.save(output_stream, format="PNG", dpi=(300, 300))
        output_stream.seek(0)
        return output_stream