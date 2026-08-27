import io
from typing import Sequence
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenPyxlImage
from app.models.product import Product
from app.services.barcode_service import BarcodeService, BarcodeConfig, BarcodeFormat

class ExcelExportService:
    @classmethod
    def generate_products_workbook(cls, products: Sequence[Product]) -> io.BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "کاتالوگ محصولات"
        ws.views.sheetView[0].rightToLeft = True  # چینش کامل راست به چپ (RTL)

        # استایل‌ها
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_font = Font(name="Tahoma", size=10, bold=True, color="FFFFFF")
        regular_font = Font(name="Tahoma", size=9)
        bold_font = Font(name="Tahoma", size=9, bold=True)
        
        thin_border = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )

        headers = [
            "ردیف", "نام کالا", "قیمت خرید (تومان)", 
            "تعداد در بسته", "قیمت مصرف‌کننده (تومان)", 
            "حاشیه سود (%)", "تصویر بارکد استاندارد"
        ]
        ws.append(headers)

        # اعمال استایل هدر
        ws.row_dimensions[1].height = 32
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # درج داده‌ها
        for row_idx, product in enumerate(products, start=2):
            ws.cell(row=row_idx, column=1, value=row_idx - 1)
            ws.cell(row=row_idx, column=2, value=product.title)
            ws.cell(row=row_idx, column=3, value=f"{int(product.cost_price):,}")
            ws.cell(row=row_idx, column=4, value=product.units_per_pack)
            ws.cell(row=row_idx, column=5, value=f"{int(product.consumer_price):,}")
            ws.cell(row=row_idx, column=6, value=f"{product.profit_margin_percent}%")

            # تولید بارکد In-Memory
            b_format = BarcodeFormat.EAN13 if len(product.barcode_value) in (12, 13) else BarcodeFormat.CODE128
            b_config = BarcodeConfig(
                title=product.title,
                code_value=product.barcode_value,
                format_type=b_format,
                barcode_height_px=90,
                title_font_size=16,
                code_font_size=14,
                margin=10
            )
            img_stream = BarcodeService.generate_barcode_image(b_config)
            
            # الصاق تصویر به سلول
            img = OpenPyxlImage(img_stream)
            img.width = 140
            img.height = 65
            ws.row_dimensions[row_idx].height = 55
            ws.add_image(img, f"G{row_idx}")

            # فرمت سلول‌های متنی
            for col_idx in range(1, 7):
                c = ws.cell(row=row_idx, column=col_idx)
                c.font = regular_font if col_idx != 2 else bold_font
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.border = thin_border

        # تنظیم پهنای ستون‌ها
        widths = {'A': 8, 'B': 32, 'C': 20, 'D': 15, 'E': 22, 'F': 16, 'G': 24}
        for col_letter, width in widths.items():
            ws.column_dimensions[col_letter].width = width

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output