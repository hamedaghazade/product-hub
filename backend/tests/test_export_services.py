import io
import pytest
from app.services.excel_service import ExcelExportService
from app.services.pdf_service import PDFExportService

@pytest.fixture
def sample_products():
    return [
        {
            "title": "شیر کم چرب کاله",
            "cost_price": 28000,
            "units_per_pack": 12,
            "barcode_value": "6261234567890",
            "consumer_price": 35000
        },
        {
            "title": "پنیر فتا صباح",
            "cost_price": 45000,
            "units_per_pack": 24,
            "barcode_value": "PROD-554433",
            "consumer_price": 52000
        }
    ]

def test_excel_export(sample_products):
    stream = ExcelExportService.create_products_sheet(sample_products)
    assert isinstance(stream, io.BytesIO)
    assert stream.getbuffer().nbytes > 0

def test_pdf_export(sample_products):
    stream = PDFExportService.generate_products_catalog(sample_products)
    assert isinstance(stream, io.BytesIO)
    assert stream.getbuffer().nbytes > 0
    # بررسی هدر PDF
    stream.seek(0)
    assert stream.read(4) == b"%PDF"