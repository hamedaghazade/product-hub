import io
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

class BarcodeEngine:
    @staticmethod
    def validate_ean13(code: str) -> bool:
        if not (isinstance(code, str) and len(code) == 13 and code.isdigit()):
            return False
        digits = [int(d) for d in code]
        checksum = sum(digits[i] if i % 2 == 0 else digits[i] * 3 for i in range(12))
        calculated_check_digit = (10 - (checksum % 10)) % 10
        return calculated_check_digit == digits[-1]

    @classmethod
    def generate_barcode_image(cls, title: str, barcode_val: str) -> io.BytesIO:
        code_type = 'ean13' if cls.validate_ean13(barcode_val) else 'code128'
        barcode_class = barcode.get_barcode_class(code_type)
        
        # تولید بارکد بدون متن پیش‌فرض برای کنترل کامل رندر متن
        writer = ImageWriter()
        writer_options = {
            'write_text': False,
            'module_height': 15.0,
            'module_width': 0.3,
            'quiet_zone': 2.0
        }
        
        raw_barcode = barcode_class(barcode_val, writer=writer)
        barcode_img = raw_barcode.render(writer_options)

        # محاسبه ابعاد نهایی برای افزودن متن بالا و پایین
        width, height = barcode_img.size
        top_padding = 40
        bottom_padding = 35
        total_height = height + top_padding + bottom_padding
        
        canvas = Image.new('RGB', (width, total_height), color='white')
        canvas.paste(barcode_img, (0, top_padding))
        
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 16)
        except OSError:
            font = ImageFont.load_default()

        # فرمت‌بندی متن فارسی برای رندر صحیح (RTL Reshaping)
        reshaped_text = arabic_reshaper.reshape(title)
        bidi_title = get_display(reshaped_text)

        # رسم متن بالای بارکد (نام کالا)
        title_bbox = draw.textbbox((0, 0), bidi_title, font=font)
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_w) / 2, 10), bidi_title, fill='black', font=font)

        # رسم عدد بارکد در پایین
        code_bbox = draw.textbbox((0, 0), barcode_val, font=font)
        code_w = code_bbox[2] - code_bbox[0]
        draw.text(((width - code_w) / 2, height + top_padding + 5), barcode_val, fill='black', font=font)

        output_buffer = io.BytesIO()
        canvas.save(output_buffer, format='PNG', dpi=(300, 300))
        output_buffer.seek(0)
        return output_buffer