import io
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import arabic_reshaper
from bidi.algorithm import get_display

class BarcodeService:
    @staticmethod
    def _fix_persian_text(text: str) -> str:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    @classmethod
    def generate_barcode_image(cls, barcode_val: str, title: str) -> io.BytesIO:
        """
        Renders Code128 barcode with product title on TOP and barcode value on BOTTOM.
        Returns In-Memory BytesIO buffer.
        """
        code_type = "code128" if len(barcode_val) != 13 else "ean13"
        try:
            barcode_class = barcode.get_barcode_class(code_type)
        except barcode.errors.BarcodeNotFoundError:
            barcode_class = barcode.get_barcode_class("code128")

        writer = ImageWriter()
        writer.font_path = None  # Use default raster font for raw barcode
        
        # 1. Render base barcode lines without text
        base_img = barcode_class(barcode_val, writer=writer).render(
            writer_options={
                "write_text": False,
                "module_width": 0.25,
                "module_height": 12.0,
                "quiet_zone": 2.0
            }
        )

        # 2. Expand Canvas for Top Title & Bottom Text
        canvas_width = max(base_img.width + 40, 320)
        canvas_height = base_img.height + 70
        canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
        draw = ImageDraw.Draw(canvas)

        # 3. Paste Barcode Image Centered
        x_offset = (canvas_width - base_img.width) // 2
        canvas.paste(base_img, (x_offset, 35))

        # 4. Draw Header (Product Title)
        persian_title = cls._fix_persian_text(title)
        draw.text((canvas_width / 2, 18), persian_title, fill="black", anchor="mm")

        # 5. Draw Footer (Barcode Number)
        draw.text((canvas_width / 2, canvas_height - 18), barcode_val, fill="black", anchor="mm")

        output = io.BytesIO()
        canvas.save(output, format="PNG", dpi=(300, 300))
        output.seek(0)
        return output\n