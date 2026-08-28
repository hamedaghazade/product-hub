import io
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

class BarcodeService:
    @staticmethod
    def generate_barcode_image(title: str, barcode_value: str) -> io.BytesIO:
        """
        تولید تصویر بارکد در حافظه با عنوان فارسی در بالا و مقدار بارکد در پایین.
        """
        barcode_val = str(barcode_value).strip()
        is_ean13 = len(barcode_val) == 13 and barcode_val.isdigit()
        barcode_type = 'ean13' if is_ean13 else 'code128'
        
        barcode_class = barcode.get_barcode_class(barcode_type)
        writer = ImageWriter()
        writer.font_path = None
        
        raw_barcode = barcode_class(barcode_val, writer=writer)
        barcode_img: Image.Image = raw_barcode.render(writer_options={
            "write_text": False,
            "quiet_zone": 2.0,
            "module_height": 12.0
        })

        width, height = barcode_img.size
        extra_top = 40
        extra_bottom = 35
        new_height = height + extra_top + extra_bottom

        final_img = Image.new("RGB", (width, new_height), "white")
        final_img.paste(barcode_img, (0, extra_top))

        draw = ImageDraw.Draw(final_img)

        # اصلاح متون فارسی برای اتصال حروف و راست‌چین‌سازی
        reshaped_title = arabic_reshaper.reshape(title)
        bidi_title = get_display(reshaped_title)

        font = ImageFont.load_default()

        # درج عنوان در بالا (وسط‌چین)
        draw.text((width // 2, extra_top // 2), bidi_title, fill="black", anchor="mm", font=font)
        # درج عدد بارکد در پایین (وسط‌چین)
        draw.text((width // 2, height + extra_top + (extra_bottom // 2)), barcode_val, fill="black", anchor="mm", font=font)

        output = io.BytesIO()
        final_img.save(output, format="PNG", optimize=True)
        output.seek(0)
        return output