import io
import os
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional

import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

logger = logging.getLogger("product_hub.barcode")

class BarcodeFormat(str, Enum):
    EAN13 = "ean13"
    UPCA = "upca"
    CODE128 = "code128"
    ITF14 = "itf14"
    GS1_128 = "gs1_128"

@dataclass
class BarcodeConfig:
    title: str = "نام کالا"
    code_value: str = "626012345678"
    format_type: BarcodeFormat = BarcodeFormat.CODE128
    title_font_path: Optional[str] = "assets/fonts/Vazirmatn-Bold.ttf"
    code_font_path: Optional[str] = "assets/fonts/Vazirmatn-Regular.ttf"
    title_font_size: int = 24
    code_font_size: int = 20
    barcode_height_px: int = 130
    module_width_mm: float = 0.4
    margin: int = 20
    foreground_color: str = "#000000"
    background_color: str = "#FFFFFF"

# آبجکت پیش‌فرض جهت رفع خطای ایمپورت در روت‌ها
global_barcode_config = BarcodeConfig()

class BarcodeService:
    @staticmethod
    def _calculate_ean13_checksum(code12: str) -> str:
        """محاسبه رقم کنترل برای کد ۱۲ رقمی EAN-13 بر اساس فرمول استاندارد"""
        odd_sum = sum(int(code12[i]) for i in range(0, 12, 2))
        even_sum = sum(int(code12[i]) for i in range(1, 12, 2))
        total = odd_sum + (even_sum * 3)
        checksum = (10 - (total % 10)) % 10
        return str(checksum)

    @classmethod
    def _validate_and_normalize_code(cls, raw_code: str, format_type: BarcodeFormat) -> str:
        """اعتبارسنجی طول و کاراکترها بر اساس نوع استاندارد"""
        code_str = str(raw_code).strip()
        
        if format_type in (BarcodeFormat.CODE128, BarcodeFormat.GS1_128):
            if not code_str:
                raise ValueError("مقدار بارکد نمی‌تواند خالی باشد.")
            return code_str

        digits_only = "".join(filter(str.isdigit, code_str))
        
        if format_type == BarcodeFormat.EAN13:
            if len(digits_only) == 12:
                return digits_only + cls._calculate_ean13_checksum(digits_only)
            elif len(digits_only) == 13:
                expected_check = cls._calculate_ean13_checksum(digits_only[:12])
                if digits_only[12] != expected_check:
                    return digits_only[:12] + expected_check
                return digits_only
            elif len(digits_only) < 12:
                padded = digits_only.zfill(12)
                return padded + cls._calculate_ean13_checksum(padded)
            else:
                trimmed = digits_only[:12]
                return trimmed + cls._calculate_ean13_checksum(trimmed)

        elif format_type == BarcodeFormat.UPCA:
            if len(digits_only) in (11, 12):
                return digits_only[:11]
            return digits_only.zfill(11)[:11]

        elif format_type == BarcodeFormat.ITF14:
            if len(digits_only) in (13, 14):
                return digits_only[:13].zfill(13)
            return digits_only.zfill(13)[:13]

        return digits_only

    @staticmethod
    def _reshape_persian_text(text: str) -> str:
        """اتصال حروف فارسی و اعمال BiDi جهت رندر صحیح در Pillow"""
        if not text:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text

    @staticmethod
    def _get_font(font_path: Optional[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """لود ایمن فونت با مکانیزم Fallback چند لایه"""
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass

        system_fallbacks = [
            "C:\\Windows\\Fonts\\tahoma.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\seguisb.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        for path in system_fallbacks:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue

        return ImageFont.load_default()

    @classmethod
    def generate_barcode_image(cls, config: BarcodeConfig) -> io.BytesIO:
        """تولید بوم تصویر شامل متن بالا، خطوط بارکد، و ارقام پایین"""
        validated_code = cls._validate_and_normalize_code(config.code_value, config.format_type)

        barcode_map = {
            BarcodeFormat.EAN13: "ean13",
            BarcodeFormat.UPCA: "upca",
            BarcodeFormat.CODE128: "code128",
            BarcodeFormat.ITF14: "itf",
            BarcodeFormat.GS1_128: "code128"
        }

        barcode_class_name = barcode_map.get(config.format_type, "code128")
        barcode_cls = barcode.get_barcode_class(barcode_class_name)

        writer = ImageWriter()
        writer.format = "PNG"

        render_input = validated_code[:12] if config.format_type == BarcodeFormat.EAN13 else validated_code
        barcode_obj = barcode_cls(render_input, writer=writer)

        raw_barcode_img: Image.Image = barcode_obj.render(
            writer_options={
                "module_width": config.module_width_mm,
                "module_height": max(10.0, config.barcode_height_px / 10.0),
                "quiet_zone": 1.0,
                "write_text": False,
                "foreground": config.foreground_color,
                "background": config.background_color,
            }
        ).convert("RGBA")

        title_font = cls._get_font(config.title_font_path, config.title_font_size)
        code_font = cls._get_font(config.code_font_path, config.code_font_size)

        dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        persian_title = cls._reshape_persian_text(config.title)
        display_code = barcode_obj.get_fullcode() if hasattr(barcode_obj, "get_fullcode") else validated_code

        t_bbox = dummy_draw.textbbox((0, 0), persian_title, font=title_font)
        title_w, title_h = t_bbox[2] - t_bbox[0], max(t_bbox[3] - t_bbox[1], config.title_font_size)

        c_bbox = dummy_draw.textbbox((0, 0), display_code, font=code_font)
        code_w, code_h = c_bbox[2] - c_bbox[0], max(c_bbox[3] - c_bbox[1], config.code_font_size)

        content_width = max(raw_barcode_img.width, title_w, code_w)
        total_width = content_width + (config.margin * 2)
        vertical_spacing = 12

        total_height = (
            config.margin +
            title_h +
            vertical_spacing +
            raw_barcode_img.height +
            vertical_spacing +
            code_h +
            config.margin
        )

        canvas = Image.new("RGBA", (int(total_width), int(total_height)), config.background_color)
        draw = ImageDraw.Draw(canvas)

        # رسم عنوان فارسی در بالا
        title_x = (total_width - title_w) // 2
        title_y = config.margin
        draw.text((title_x, title_y), persian_title, font=title_font, fill=config.foreground_color)

        # قرار دادن بارکد در وسط
        barcode_x = (total_width - raw_barcode_img.width) // 2
        barcode_y = title_y + title_h + vertical_spacing
        canvas.paste(raw_barcode_img, (int(barcode_x), int(barcode_y)), raw_barcode_img)

        # رسم رقم در پایین
        code_x = (total_width - code_w) // 2
        code_y = barcode_y + raw_barcode_img.height + vertical_spacing
        draw.text((code_x, code_y), display_code, font=code_font, fill=config.foreground_color)

        output_buffer = io.BytesIO()
        canvas.convert("RGB").save(output_buffer, format="PNG", quality=100)
        output_buffer.seek(0)
        return output_buffer

# تعریف نام‌های مستعار و متغیرهای سازگاری
BarcodeEngine = BarcodeService