import io
import os
from typing import Sequence
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

from app.models.product import Product
from app.services.barcode_service import BarcodeService, BarcodeConfig, BarcodeFormat

class PDFExportService:
    @staticmethod
    def _reshape(text: str) -> str:
        if not text:
            return ""
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)

    @classmethod
    def generate_products_pdf(cls, products: Sequence[Product]) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        # ثبت فونت فارسی
        font_path = "assets/fonts/Vazirmatn-Regular.ttf"
        font_name = "Helvetica"
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont("Vazirmatn", font_path))
                font_name = "Vazirmatn"
            except Exception:
                pass

        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=16,
            leading=22,
            alignment=1, # Center
            textColor=colors.HexColor("#0F172A")
        )
        
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=12,
            alignment=1, # Center
            textColor=colors.HexColor("#1E293B")
        )

        # تیتر گزارش
        elements.append(Paragraph(cls._reshape("گزارش کاتالوگ و بارکد محصولات سامانه Product Hub"), title_style))
        elements.append(Spacer(1, 15))

        # ساختار جدول
        headers = [
            cls._reshape("تصویر بارکد"),
            cls._reshape("حاشیه سود"),
            cls._reshape("قیمت مصرف‌کننده"),
            cls._reshape("تعداد در بسته"),
            cls._reshape("قیمت خرید"),
            cls._reshape("نام محصول"),
            cls._reshape("ردیف")
        ]

        table_data = [headers]

        for idx, prod in enumerate(products, start=1):
            # تولید بارکد برای PDF
            b_format = BarcodeFormat.EAN13 if len(prod.barcode_value) in (12, 13) else BarcodeFormat.CODE128
            b_config = BarcodeConfig(
                title=prod.title,
                code_value=prod.barcode_value,
                format_type=b_format,
                barcode_height_px=70,
                title_font_size=14,
                code_font_size=12,
                margin=5
            )
            img_stream = BarcodeService.generate_barcode_image(b_config)
            barcode_img = RLImage(img_stream, width=120, height=45)

            row = [
                barcode_img,
                Paragraph(f"%{prod.profit_margin_percent}", cell_style),
                Paragraph(f"{int(prod.consumer_price):,} " + cls._reshape("تومان"), cell_style),
                Paragraph(str(prod.units_per_pack), cell_style),
                Paragraph(f"{int(prod.cost_price):,} " + cls._reshape("تومان"), cell_style),
                Paragraph(cls._reshape(prod.title), cell_style),
                Paragraph(str(idx), cell_style)
            ]
            table_data.append(row)

        table = Table(table_data, colWidths=[130, 80, 110, 75, 110, 190, 45])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer