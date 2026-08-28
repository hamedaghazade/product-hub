import io
from typing import Any, Dict, List
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as ReportLabImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from app.services.barcode_service import BarcodeService

class PDFExportService:
    @staticmethod
    def _fix_text(text: str) -> str:
        if not text:
            return ""
        return get_display(arabic_reshaper.reshape(str(text)))

    @classmethod
    def generate_products_catalog(cls, products: List[Dict[str, Any]]) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20,
            leftMargin=20,
            topMargin=25,
            bottomMargin=20
        )

        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Normal"],
            alignment=1,
            fontSize=15,
            leading=18
        )

        elements.append(Paragraph(cls._fix_text("کاتالوگ محصولات و بارکدها"), title_style))
        elements.append(Spacer(1, 15))

        table_data = [[
            cls._fix_text("تصویر بارکد"),
            cls._fix_text("قیمت مصرف‌کننده"),
            cls._fix_text("بسته‌بندی"),
            cls._fix_text("قیمت پایه"),
            cls._fix_text("کد بارکد"),
            cls._fix_text("نام محصول")
        ]]

        for item in products:
            img_stream = BarcodeService.generate_barcode_image(item["title"], str(item["barcode_value"]))
            rl_img = ReportLabImage(img_stream, width=110, height=45)

            row = [
                rl_img,
                f"{float(item['consumer_price']):,.0f}",
                str(item["units_per_pack"]),
                f"{float(item['cost_price']):,.0f}",
                str(item["barcode_value"]),
                cls._fix_text(item["title"])
            ]
            table_data.append(row)

        table = Table(table_data, colWidths=[120, 95, 60, 95, 90, 95])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ]))

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer