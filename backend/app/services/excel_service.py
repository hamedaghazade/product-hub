import io
from typing import Any, Dict, List
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from app.services.barcode_service import BarcodeService

class ExcelExportService:
    @staticmethod
    def create_products_sheet(products: List[Dict[str, Any]]) -> io.BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "محصولات"
        ws.views.sheetView[0].rightToLeft = True

        headers = [
            "ردیف",
            "نام کالا",
            "قیمت پایه (تومان)",
            "تعداد در بسته",
            "قیمت مصرف‌کننده (تومان)",
            "کد بارکد",
            "تصویر بارکد"
        ]
        ws.append(headers)

        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font = Font(name="Tahoma", size=10, bold=True, color="FFFFFF")
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style="thin", color="D1D5DB"),
            right=Side(style="thin", color="D1D5DB"),
            top=Side(style="thin", color="D1D5DB"),
            bottom=Side(style="thin", color="D1D5DB")
        )

        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = align_center
            cell.border = thin_border

        ws.row_dimensions[1].height = 28

        for row_idx, item in enumerate(products, start=2):
            ws.row_dimensions[row_idx].height = 65
            ws.append([
                row_idx - 1,
                item["title"],
                float(item["cost_price"]),
                int(item["units_per_pack"]),
                float(item["consumer_price"]),
                str(item["barcode_value"]),
                ""
            ])

            for col_idx in range(1, len(headers) + 1):
                c = ws.cell(row=row_idx, column=col_idx)
                c.alignment = align_center
                c.border = thin_border
                c.font = Font(name="Tahoma", size=9)

            # تولید تصویر بارکد و درج در سلول
            img_stream = BarcodeService.generate_barcode_image(item["title"], str(item["barcode_value"]))
            img = OpenpyxlImage(img_stream)
            img.width = 135
            img.height = 60
            ws.add_image(img, f"G{row_idx}")

        ws.column_dimensions["A"].width = 8
        ws.column_dimensions["B"].width = 28
        ws.column_dimensions["C"].width = 18
        ws.column_dimensions["D"].width = 14
        ws.column_dimensions["E"].width = 20
        ws.column_dimensions["F"].width = 18
        ws.column_dimensions["G"].width = 24

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output