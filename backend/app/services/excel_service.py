import io
from typing import List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenPyXLImage
from app.services.barcode_service import BarcodeService

class ExcelExportService:
    @staticmethod
    def generate_products_sheet(products: List[dict]) -> io.BytesIO:
        """
        تولید شیت استاندارد اکسل با بارکدهای Embed شده در سلول‌ها
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "لیست کالاها و بارکد"
        ws.views.sheetView[0].rightToLeft = True  # فعال‌سازی RTL برای اکسل

        # هدرها
        headers = ["ردیف", "نام کالا", "کد بارکد", "قیمت پایه (تومان)", "قیمت مصرف‌کننده", "تعداد در بسته", "تصویر بارکد"]
        ws.append(headers)

        # استایل‌دهی هدر
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_font = Font(name="Tahoma", size=11, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1")
        )

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        # تنظیم عرض ستون‌ها
        column_widths = {"A": 8, "B": 30, "C": 20, "D": 18, "E": 18, "F": 14, "G": 32}
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width

        # درج داده‌ها و تصاویر
        for idx, prod in enumerate(products, start=2):
            ws.row_dimensions[idx].height = 65  # ارتفاع مناسب برای قرارگیری تصویر
            
            ws.cell(row=idx, column=1, value=idx - 1).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=idx, column=2, value=prod["title"]).alignment = Alignment(horizontal="right", vertical="center")
            ws.cell(row=idx, column=3, value=prod["barcode_value"]).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=idx, column=4, value=f"{prod['cost_price']:,.0f}").alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=idx, column=5, value=f"{prod['consumer_price']:,.0f}").alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=idx, column=6, value=prod["units_per_pack"]).alignment = Alignment(horizontal="center", vertical="center")

            for col in range(1, 8):
                ws.cell(row=idx, column=col).border = thin_border

            # تولید و جایگذاری تصویر بارکد
            img_stream = BarcodeService.generate_barcode_image(prod["title"], prod["barcode_value"])
            img = OpenPyXLImage(img_stream)
            img.width = 190
            img.height = 70
            
            # درج دقیق در سلول ستون G
            ws.add_image(img, f"G{idx}")

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output