import io
from jinja2 import Template
from weasyprint import HTML
import base64
from app.services.barcode_service import BarcodeService

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <style>
        @page { size: A4 portrait; margin: 15mm; }
        body { font-family: 'Vazirmatn', Tahoma, sans-serif; direction: rtl; color: #0f172a; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #0284c7; padding-bottom: 10px; }
        h1 { margin: 0; font-size: 18px; color: #0f172a; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px; }
        th { background-color: #0284c7; color: #ffffff; padding: 8px; border: 1px solid #cbd5e1; }
        td { padding: 6px; border: 1px solid #cbd5e1; text-align: center; vertical-align: middle; }
        tr:nth-child(even) { background-color: #f8fafc; }
        .barcode-img { max-width: 140px; height: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>گزارش موجودی و کاتالوگ بارکد محصولات</h1>
    </div>
    <table>
        <thead>
            <tr>
                <th>ردیف</th>
                <th>بارکد</th>
                <th>نام کالا</th>
                <th>قیمت خرید</th>
                <th>بسته</th>
                <th>قیمت مصرف‌کننده</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ loop.index }}</td>
                <td><img class="barcode-img" src="data:image/png;base64,{{ item.barcode_base64 }}" /></td>
                <td>{{ item.title }}</td>
                <td>{{ "{:,.0f}".format(item.cost_price) }}</td>
                <td>{{ item.units_per_pack }}</td>
                <td>{{ "{:,.0f}".format(item.consumer_price) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

class PDFService:
    @staticmethod
    def generate_products_pdf(products: list) -> io.BytesIO:
        items_payload = []
        for p in products:
            img_buf = BarcodeService.generate_barcode_image(p.barcode_value, p.title)
            b64_str = base64.b64encode(img_buf.getvalue()).decode()
            items_payload.append({
                "title": p.title,
                "cost_price": p.cost_price,
                "units_per_pack": p.units_per_pack,
                "consumer_price": p.consumer_price,
                "barcode_base64": b64_str
            })

        template = Template(HTML_TEMPLATE)
        rendered_html = template.render(items=items_payload)

        pdf_io = io.BytesIO()
        HTML(string=rendered_html).write_pdf(pdf_io)
        pdf_io.seek(0)
        return pdf_io\n