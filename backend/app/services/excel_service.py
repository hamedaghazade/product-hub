import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenPyxlImage
from app.services.barcode_service import BarcodeService

class ExcelService:
    @staticmethod
    def generate_products_sheet(products: list) -> io.BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "لیست محصولات"
        ws.views.sheetView[0].rightToLeft = True

        headers = ["شناسه", "تصویر بارکد", "نام کالا", "قیمت خرید (ریال)", "تعداد در بسته", "قیمت مصرف‌کننده (ریال)", "کد بارکد"]
        ws.append(headers)

        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_font = Font(name="Tahoma", size=10, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        for col_num, _ in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.row_dimensions[1].height = 28
        col_widths = {"A": 8, "B": 24, "C": 30, "D": 18, "E": 14, "F": 20, "G": 18}
        for col_letter, width in col_widths.items():
            ws.column_dimensions[col_letter].width = width

        for idx, item in enumerate(products, start=2):
            ws.row_dimensions[idx].height = 65
            ws.cell(row=idx, column=1, value=item.id)
            ws.cell(row=idx, column=3, value=item.title)
            ws.cell(row=idx, column=4, value=item.cost_price)
            ws.cell(row=idx, column=5, value=item.units_per_pack)
            ws.cell(row=idx, column=6, value=item.consumer_price)
            ws.cell(row=idx, column=7, value=item.barcode_value)

            # Insert In-Memory Barcode Image
            img_stream = BarcodeService.generate_barcode_image(item.barcode_value, item.title)
            img = OpenPyxlImage(img_stream)
            img.width = 160
            img.height = 70
            ws.add_image(img, f"B{idx}")

            for col_num in range(1, 8):
                c = ws.cell(row=idx, column=col_num)
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.border = thin_border
                c.font = Font(name="Tahoma", size=10)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output\n