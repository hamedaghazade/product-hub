import os
from io import BytesIO
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

from app.services.barcode_service import BarcodeService, get_persian_font

class PDFExportService:
    _font_registered = False
    _registered_font_name = "Helvetica"

    @classmethod
    def _register_persian_font(cls) -> str:
        """ثبت سراسری فونت فارسی TTF در ReportLab"""
        if cls._font_registered:
            return cls._registered_font_name

        search_paths = [
            os.getenv("PERSIAN_FONT_PATH", "assets/fonts/Vazirmatn-Regular.ttf"),
            os.getenv("PERSIAN_FONT_BOLD_PATH", "assets/fonts/Vazirmatn-Bold.ttf"),
            "backend/assets/fonts/Vazirmatn-Regular.ttf",
            "backend/assets/fonts/Vazirmatn-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]

        for path in search_paths:
            if os.path.exists(path):
                try:
                    font_name = "Vazirmatn"
                    pdfmetrics.registerFont(TTFont(font_name, path))
                    cls._registered_font_name = font_name
                    cls._font_registered = True
                    return font_name
                except Exception:
                    continue

        cls._registered_font_name = "Helvetica"
        return "Helvetica"

    @classmethod
    def _fa(cls, text: Any) -> str:
        """تبدیل و راست‌چین‌سازی رشته‌های متنی و ارقام برای PDF"""
        if text is None:
            return ""
        raw_str = str(text).strip()
        if not raw_str:
            return ""
        reshaped = arabic_reshaper.reshape(raw_str)
        return get_display(reshaped)

    @classmethod
    def generate_pdf_catalog(cls, products: List[Dict[str, Any]]) -> BytesIO:
        font_name = cls._register_persian_font()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="PDFRTLTitle",
            fontName=font_name,
            fontSize=16,
            leading=22,
            alignment=1, # Center
            textColor=colors.HexColor("#0F172A")
        )

        header_style = ParagraphStyle(
            name="PDFRTLHeader",
            fontName=font_name,
            fontSize=10,
            leading=14,
            alignment=1,
            textColor=colors.white
        )

        cell_style = ParagraphStyle(
            name="PDFRTLCell",
            fontName=font_name,
            fontSize=9,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#1E293B")
        )

        title_cell_style = ParagraphStyle(
            name="PDFRTLTitleCell",
            fontName=font_name,
            fontSize=9,
            leading=13,
            alignment=2, # Right aligned for item names
            textColor=colors.HexColor("#0F172A")
        )

        elements = []
        elements.append(Paragraph(cls._fa("کاتالوگ و فهرست رسمی محصولات"), title_style))
        elements.append(Spacer(1, 15))

        # ساختار ستون‌های RTL: ردیف اول از راست به چپ
        headers = [
            Paragraph(cls._fa("تصویر بارکد"), header_style),
            Paragraph(cls._fa("قیمت مصرف‌کننده"), header_style),
            Paragraph(cls._fa("تعداد در بسته"), header_style),
            Paragraph(cls._fa("قیمت خرید"), header_style),
            Paragraph(cls._fa("نام کالا"), header_style),
            Paragraph(cls._fa("ردیف"), header_style),
        ]

        table_data = [headers]

        for idx, item in enumerate(products, start=1):
            barcode_stream = BarcodeService.generate_barcode_image(
                title=item.get("title", ""),
                barcode_value=str(item.get("barcode_value", ""))
            )
            img = RLImage(barcode_stream, width=130, height=52)

            cost_val = int(item.get('cost_price', 0))
            cons_val = int(item.get('consumer_price', 0))

            cost_str = f"{cost_val:,} {cls._fa('تومان')}"
            cons_str = f"{cons_val:,} {cls._fa('تومان')}"

            row = [
                img,
                Paragraph(cls._fa(cons_str), cell_style),
                Paragraph(cls._fa(str(item.get("units_per_pack", 1))), cell_style),
                Paragraph(cls._fa(cost_str), cell_style),
                Paragraph(cls._fa(item.get("title", "")), title_cell_style),
                Paragraph(cls._fa(str(idx)), cell_style)
            ]
            table_data.append(row)

        table = Table(table_data, colWidths=[135, 95, 60, 95, 140, 30])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer