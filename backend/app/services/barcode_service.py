import io
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

class BarcodeService:
    @staticmethod
    def generate_barcode_image(
        title: str,
        barcode_value: str,
        font_path: str = "assets/fonts/Vazirmatn-Bold.ttf"
    ) -> io.BytesIO:
        """
        تولید تصویر بارکد با عنوان فارسی در بالا و کد در پایین به صورت In-Memory
        """
        # ۱. تعیین نوع بارکد (EAN-13 یا Code128)
        if barcode_value.isdigit() and len(barcode_value) == 13:
            barcode_class = barcode.get_barcode_class("ean13")
        else:
            barcode_class = barcode.get_barcode_class("code128")

        writer = ImageWriter()
        writer.format = "PNG"
        
        # تولید بارکد بدون متن پیش‌فرض کتابخانه برای کنترل کامل روی تایپوگرافی
        options = {
            "write_text": False,
            "module_height": 14.0,
            "module_width": 0.35,
            "quiet_zone": 2.5,
        }
        
        raw_barcode = barcode_class(barcode_value, writer=writer)
        barcode_buffer = io.BytesIO()
        raw_barcode.write(barcode_buffer, options=options)
        barcode_buffer.seek(0)
        
        # ۲. باز کردن تصویر بارکد در Pillow
        barcode_img = Image.open(barcode_buffer).convert("RGBA")
        bw, bh = barcode_img.size

        # ۳. آماده‌سازی متن فارسی (Reshaping & BiDi)
        reshaped_text = arabic_reshaper.reshape(title)
        bidi_title = get_display(reshaped_text)

        # بارگذاری فونت
        try:
            title_font = ImageFont.truetype(font_path, size=24)
            code_font = ImageFont.truetype(font_path, size=20)
        except IOError:
            title_font = ImageFont.load_default()
            code_font = ImageFont.load_default()

        # ۴. ابعاد بوم جدید (افزودن مارجین برای متن بالا و پایین)
        top_padding = 45
        bottom_padding = 40
        canvas_width = max(bw, 420)
        canvas_height = bh + top_padding + bottom_padding

        canvas = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        # درج بارکد در مرکز بوم
        barcode_x = (canvas_width - bw) // 2
        canvas.paste(barcode_img, (barcode_x, top_padding), barcode_img)

        # محاسبه موقعیت متن عنوان (بالا - وسط‌چین)
        title_bbox = draw.textbbox((0, 0), bidi_title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(((canvas_width - title_w) // 2, 10), bidi_title, fill=(15, 23, 42), font=title_font)

        # محاسبه موقعیت متن کد بارکد (پایین - وسط‌چین)
        code_bbox = draw.textbbox((0, 0), barcode_value, font=code_font)
        code_w = code_bbox[2] - code_bbox[0]
        draw.text(((canvas_width - code_w) // 2, bh + top_padding + 5), barcode_value, fill=(51, 65, 85), font=code_font)

        # ۵. خروجی در قالب BytesIO
        output_buffer = io.BytesIO()
        canvas.convert("RGB").save(output_buffer, format="PNG", dpi=(300, 300))
        output_buffer.seek(0)
        return output_buffer